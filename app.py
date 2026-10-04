"""NASA POWER + Prophet ile Hava Durumu ve YZ Asistanı (OOP Mimarisi)."""
import json
import logging
import threading
import time
import os
from datetime import date, timedelta

import pandas as pd
import requests
import google.generativeai as genai
from flask import Flask, jsonify, request, send_from_directory
from prophet import Prophet
from dotenv import load_dotenv

class WeatherForecaster:
    """NASA verilerini çeken ve Prophet ile tahmin üreten sınıf."""
    def __init__(self):
        self.power_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.vars = {"T2M": "temp", "PRECTOTCORR": "rain", "WS2M": "wind"}
        self.cache = {}
        self.ttl = 6 * 3600  # 6 saatlik önbellek
        self.lock = threading.Lock()
        
        # Prophet loglarını sustur
        logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
        logging.getLogger("prophet").setLevel(logging.WARNING)

    def fetch_history(self, lat, lon, years=3):
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=365 * years)
        r = requests.get(self.power_url, params={
            "parameters": ",".join(self.vars.keys()), "community": "RE",
            "latitude": lat, "longitude": lon,
            "start": start.strftime("%Y%m%d"), "end": end.strftime("%Y%m%d"),
            "format": "JSON"
        }, timeout=90)
        r.raise_for_status()
        df = pd.DataFrame(r.json()["properties"]["parameter"])
        df.index = pd.to_datetime(df.index, format="%Y%m%d")
        return df.where(df != -999)

    def forecast(self, lat, lon, n_days=5):
        key = (round(lat, 2), round(lon, 2))
        with self.lock:
            hit = self.cache.get(key)
            if hit and time.time() - hit[0] < self.ttl:
                return hit[1]

        df = self.fetch_history(lat, lon)
        today = pd.Timestamp(date.today())
        days = [{"date": (today + pd.Timedelta(days=i)).strftime("%Y-%m-%d")} for i in range(n_days)]

        for col, name in self.vars.items():
            s = df[col].dropna()
            train = pd.DataFrame({"ds": s.index, "y": s.values})
            m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            m.fit(train)
            gap = max((today - train["ds"].max()).days, 0)
            pred = m.predict(m.make_future_dataframe(periods=gap + n_days))
            pred = pred[pred["ds"] >= today].head(n_days)
            for d, v in zip(days, pred["yhat"]):
                d[name] = round(max(v, 0) if name != "temp" else v, 1)

        with self.lock:
            self.cache[key] = (time.time(), days)
        return days


class ChatAssistant:
    """Gemini API ile iletişim kuran akıllı asistan sınıfı."""
    def __init__(self, model_name='gemini-3.7-flash'):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("DİKKAT: .env dosyasından API anahtarı okunamadı!")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name

    def generate_response(self, message, history, city, forecast_data):
        context = (
            f"Sen '{city}' bölgesi için uzman bir seyahat ve hava durumu asistanısın. "
            "Kısa, samimi ve Türkçe cevap ver. "
            f"Aşağıdaki 5 günlük tahmine dayanarak SADECE KULLANICININ SORDUĞU SORUYA odaklan. "
            "Eğer kullanıcı sadece kıyafet sorarsa sadece kıyafet önerisi ver. Eğer turistik yer, "
            "aktivite veya mekan önerisi isterse, SIKICI BLOK METİNLER YAZMA. Önerilerini madde işaretleri, "
            "kalın yazılar kullanarak ŞIK, SIRALI ve OKUNABİLİR bir liste halinde sun. "
            f"Ayrıca önerdiğin her mekanın {city} merkezine olan YAKLAŞIK UZAKLIĞINI "
            "(örneğin: 🚗 5 km, 🚶‍♂️ Yürüme mesafesi) mutlaka listeye ekle.\n"
            f"ÖNEMLİ KURAL: Eğer kullanıcı {city} dışında BAŞKA BİR ŞEHİR hakkında soru sorarsa, "
            "ona kibarca 'O şehrin güncel NASA verilerini görebilmem için lütfen harita üzerinden o şehre tıklayın' "
            "şeklinde yönlendirme yap.\n"
            f"Tahmin: {json.dumps(forecast_data)}\n\n"
        )
        
        model = genai.GenerativeModel(self.model_name)
        history_gemini = []
        for h in history[-10:]:
            role = "user" if h.get("role") == "user" else "model"
            if isinstance(h.get("content"), str):
                history_gemini.append({"role": role, "parts": [h.get("content")]})
        
        chat = model.start_chat(history=history_gemini)
        full_prompt = context + "Kullanıcının sorusu: " + message
        response = chat.send_message(full_prompt)
        return response.text


class WeatherApp:
    """Flask sunucusunu ve HTTP isteklerini yöneten ana uygulama sınıfı."""
    def __init__(self):
        self.app = Flask(__name__, static_folder="static")
        self.forecaster = WeatherForecaster()
        self.assistant = ChatAssistant()
        self.setup_routes()

    def parse_coords(self, src):
        try:
            lat, lon = float(src["lat"]), float(src["lon"])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        except (KeyError, TypeError, ValueError):
            pass
        return None

    def setup_routes(self):
        @self.app.get("/")
        def index():
            return send_from_directory("static", "index.html")

        @self.app.get("/api/forecast")
        def api_forecast():
            c = self.parse_coords(request.args)
            if not c:
                return jsonify(error="Geçersiz koordinat"), 400
            try:
                return jsonify(days=self.forecaster.forecast(*c))
            except Exception as e:
                return jsonify(error=f"Tahmin üretilemedi: {e}"), 502

        @self.app.post("/api/chat")
        def api_chat():
            body = request.get_json(silent=True) or {}
            msg = (body.get("message") or "").strip()
            city = body.get("city", "Bilinmeyen Konum")
            c = self.parse_coords(body)
            
            if not msg or not c:
                return jsonify(error="Mesaj veya koordinat eksik"), 400
                
            try:
                days = self.forecaster.forecast(*c)
                reply = self.assistant.generate_response(msg, body.get("history", []), city, days)
                return jsonify(reply=reply)
            except Exception as e:
                return jsonify(error=f"Chatbot hatası: {e}"), 502

    def run(self):
        self.app.run(debug=True, threaded=True)


if __name__ == "__main__":
    app_instance = WeatherApp()
    app_instance.run()