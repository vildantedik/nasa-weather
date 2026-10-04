# Türkiye Hava Durumu & NASA YZ Asistanı 🌍🌦️

Bu proje, NASA POWER API iklim verilerini ve Prophet makine öğrenmesi algoritmasını kullanarak Türkiye üzerindeki herhangi bir koordinat için 5 günlük hava durumu tahmini üreten interaktif bir web uygulamasıdır. Ayrıca Google Gemini API ile entegre çalışan ve kullanıcının seçtiği konuma özel seyahat/kıyafet/aktivite tavsiyeleri veren akıllı bir sohbet asistanı içerir. 

## 🚀 Özellikler

- **İnteraktif Harita:** Leaflet.js tabanlı harita üzerinden Türkiye sınırları içinde istenilen konuma tıklayarak anlık analiz yapabilme.
- **Yapay Zeka Tahmini:** Geçmiş 3 yıllık NASA verileri üzerinde Prophet modelini eğiterek geleceğe dönük sıcaklık, yağış ve rüzgar tahminleri oluşturma.
- **Akıllı Seyahat Asistanı:** Gemini API ile çalışan, kullanıcının seçtiği şehre ve 5 günlük hava tahminine göre dinamik öneriler (mekan, kıyafet, aktivite) sunan chatbot.
- **Canlı Radar & Uydu:** RainViewer entegrasyonu ile harita üzerinde gerçek zamanlı yağış bulutlarını izleyebilme.
- **Gerçek Zamanlı Metrikler:** Open-Meteo üzerinden anlık hava kalitesi (AQI) ölçümü ve ekstrem hava durumu uyarıları.

## 📂 Klasör Yapısı

Proje dosyaları aşağıdaki yapıya uygun olarak organize edilmiştir. Güvenlik nedeniyle API anahtarlarını barındıran `.env` dosyası GitHub'a yüklenmemiştir.

```text
├── app.py                 # Uygulamanın ana arka yüz (Flask & OOP) kodları
├── requirements.txt       # Projenin çalışması için gereken kütüphanelerin listesi
├── .gitignore             # Git versiyon kontrolü dışında bırakılan dosyalar (.env dahil)
├── README.md              # Proje dökümantasyonu
└── static/
    └── index.html         # Uygulamanın ön yüzü (HTML, CSS, JS ve Harita arayüzü)
```

## 🛠️ Kullanılan Teknolojiler

- **Arka Yüz (Backend):** Python 3, Flask, Pandas, Prophet (Makine Öğrenmesi)
- **Ön Yüz (Frontend):** HTML5, CSS3, Vanilla JavaScript, Leaflet.js, Marked.js
- **API Entegrasyonları:** Google Generative AI (Gemini), NASA POWER, Open-Meteo, RainViewer

## ⚙️ Kurulum ve Çalıştırma (Yerel Bilgisayar İçin)

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla uygulayın:

### 1. Projeyi Bilgisayarınıza İndirin

```bash
git clone https://github.com/KULLANICI_ADINIZ/projenizin-adi.git
cd projenizin-adi
```

### 2. Gerekli Kütüphaneleri Yükleyin

Python yüklü bir terminal/komut istemcisinde aşağıdaki komutu çalıştırarak `requirements.txt` içindeki tüm paketleri indirin:

```bash
pip install -r requirements.txt
```

### 3. API Anahtarınızı Ayarlayın

Projenin ana dizininde (`app.py` ile aynı klasörde) `.env` adında uzantısız bir dosya oluşturun. Google AI Studio'dan aldığınız ücretsiz API anahtarınızı içine şu formatta yapıştırın:

```env
GEMINI_API_KEY=sizin_gizli_api_anahtariniz
```

> **Not:** Bu dosya `.gitignore` listesinde olduğu için siz kendi GitHub deponuza yükleme yapsanız bile internete gönderilmeyecek ve güvende kalacaktır.

### 4. Sunucuyu Başlatın

```bash
python app.py
```

Terminalinizde sunucunun başladığını gördükten sonra tarayıcınızdan `http://127.0.0.1:5000` adresine giderek uygulamayı kullanmaya başlayabilirsiniz.

## ⚠️ Önemli Notlar

- Uygulamanın harita sınırları ve API sorguları sadece Türkiye bölgesi için yapılandırılmıştır.
- Sistemde Google'ın ücretsiz `gemini-3.7-flash` (veya benzeri desteklenen flash modelleri) kullanılmaktadır. Yoğun kullanımda ücretsiz günlük kota dolduğunda chatbot geçici olarak yanıt vermeyi durdurabilir.
