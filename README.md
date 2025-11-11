# 📺 YouTube Video Özetleyici

YouTube videolarının başlık, açıklama ve altyazı içeriklerini analiz ederek **Google Gemini** modeli ile detaylı ve anlaşılır özetler oluşturan bir web aracıdır.

---
## 🚀 Özellikler
- ✅ YouTube video linki ile otomatik özet alma
- ✅ Türkçe ve İngilizce altyazı desteği
- ✅ Otomatik altyazı çözümleme
- ✅ Başlık + Açıklama + Transkript analizi
- ✅ Sade, anlaşılır ve maddeli özet yapısı
- ✅ Streamlit tabanlı kolay web arayüzü

---
## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Açıklama |
|----------|----------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) | Projenin ana programlama dili |
| ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=flat&logo=google&logoColor=white) | Yapay zeka modeli ile özet oluşturma |
| ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) | Web arayüzü oluşturma |
| ![pytubefix](https://img.shields.io/badge/pytubefix-FFDD00?style=flat) | YouTube video bilgisi ve altyazı verilerini alma |
| ![dotenv](https://img.shields.io/badge/python--dotenv-4E9A06?style=flat) | API anahtarlarını güvenli şekilde yönetme |

---
## 📦 Proje Yapısı

```
📦 Proje Klasörü
│
├── venv/         # Sanal ortam 
├── .env          # API anahtarı 
└── youtube.py    # Uygulama dosyası
```
---
## 🛠️ Gerekli Kurulumlar

### 1️⃣ Sanal Ortam Oluşturma

Proje klasörünüzü açtıktan sonra aşağıdaki komutları sırayla çalıştırın:
```bash
python -m venv venv
```

### 2️⃣ Sanal Ortamı Aktif Etme 

```bash
Windows için:
.\venv\Scripts\activate
```
```bash
Mac / Linux için:
source venv/bin/activate
```
### 3️⃣ Gerekli Kütüphanelerin Kurulumu
```bash
pip install streamlit pytubefix google-generativeai python-dotenv
```
### 🔑 API Anahtarı Ekleme

Proje klasörüne .env adında bir dosya oluşturun ve içine aşağıdaki satırı ekleyin:
```bash
API_KEY="YOUR_API_KEY"
```
### ▶️ Uygulamayı Çalıştırma
```bash
streamlit run youtube.py
```
---


## 📱 Ekran Görüntüleri

|  | 
|----------------------|
| ![Login](screenshots/ozet.png) 



| |  
|----------------------|
| ![Login](screenshots/ozet2.png) |

---

