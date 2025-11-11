import os
import re
import time
import logging
import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
import google.generativeai as genai
from dotenv import load_dotenv

# --- Yapılandırma ---
load_dotenv()

# Basit loglama
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Gemini API Konfigürasyonu ---
try:
    genai.configure(api_key=os.getenv("API_KEY"))

    generation_config = {
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 40,
      
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
    ]
    

    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    logger.info("Gemini Modeli başarıyla yüklendi.")
except Exception as e:
    logger.error(f"Gemini modeli yüklenirken hata oluştu: {e}")
    model = None

# --- Yardımcı Fonksiyonlar ---

def is_valid_youtube_url(url):
    """Geçerli bir YouTube URL'si olup olmadığını kontrol eder."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    return re.match(youtube_regex, url) is not None

def clean_text(text, max_length=15000):
    """Metni AI modeli için temizler ve kısaltır."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    return text[:max_length]

def get_youtube_transcript(yt):
    """YouTube videosundan transkripti (altyazıyı) alır."""
    try:
        # Önce Türkçe, sonra İngilizce, sonra otomatik altyazıyı dene
        caption = None
        for lang_code in ['tr', 'en', 'a.tr', 'a.en']:
            try:
                caption = yt.captions.get_by_language_code(lang_code)
                if caption:
                    logger.info(f"Altyazı bulundu: {lang_code}")
                    break
            except:
                continue
        
        if caption:
            # SRT formatındaki altyazıları al ve temizle
            srt_text = caption.generate_srt_captions()
            # Zaman damgalarını ve satır numaralarını kaldır
            lines = []
            for line in srt_text.split('\n'):
                # Satır numarası veya zaman damgası değilse ekle
                if not re.match(r'^\d+$', line.strip()) and not re.match(r'\d{2}:\d{2}:\d{2}', line):
                    if line.strip():
                        lines.append(line.strip())
            
            return ' '.join(lines)
        else:
            logger.warning("Video için altyazı bulunamadı.")
            return ""
            
    except Exception as e:
        logger.warning(f"Transkript alınamadı: {str(e)}")
        return ""

def generate_summary_prompt(text):
    """Gemini AI için özetleme komutunu oluşturur."""
    return f"""Aşağıdaki YouTube videosu içeriğini (Başlık, Açıklama ve Transkript) detaylı bir şekilde Türkçe olarak özetle:
    
    {text}
    
    Özetleme Kuralları:
    1-Video içeriğini kendi yorumunu katmadan, sadece videoda verilen bilgilere dayanarak özetle.
    2-Önemli kavramları, tanımları, verilen örnekleri ve çıkarılacak dersleri açıkça belirt.
    3-Gereksiz ayrıntıları, gereksiz tekrarları, kişisel sohbetleri ve laf kalabalığını çıkar.
    4-Özet, kronolojik veya kavramsal olarak düzenli olmalı.
    5-Eğer videoda aşamalar, maddeler veya adımlar varsa, bunları maddeler halinde açıkça belirt.
    6-Teknik bir konu anlatılıyorsa, tanımı → amacı → nasıl yapılır → dikkat edilmesi gerekenler sıralamasına göre düzenle.
    7-Cümleler kısa, sade ve anlaşılır olmalı. Karmaşık akademik dil kullanma.
    8-Nesnel bir ton kullan. Duygu katma, abartma, kişisel fikir ekleme.
    9-Videoda sayılar, istatistikler, önemli formüller veya isimler varsa aynen koru.
    10-Videoda mizah, kişisel hikaye veya uzun sohbet varsa sadece ana fikrini kısaca belirt, detay anlatma."""


# --- Streamlit Arayüzü ---

st.set_page_config(page_title="YouTube Özetleyici", page_icon="📺", layout="wide")
st.title("📺 YouTube Video Özetleyici")
st.caption("Video linkini yapıştırın ve anında detaylı bir özet alın.")

# Yan bilgi kutusu
with st.sidebar:
    st.header("ℹ️ Bilgi")
    st.markdown("""
    **Desteklenen Özellikler:**
    - ✅ Türkçe ve İngilizce altyazılar
    - ✅ Otomatik altyazı desteği
    - ✅ Video başlık ve açıklama analizi
    - ✅ AI destekli özetleme
    
    **Not:** Video altyazısı yoksa ve açıklama boşsa özetleme yapılamaz.
    """)

# Model yüklenemezse hata göster
if not model:
    st.error("🚨 AI Modeli yüklenemedi. Lütfen API anahtarınızı kontrol edin.")
else:
    # URL giriş alanı
    video_url = st.text_input("YouTube Video URL'si", placeholder="https://www.youtube.com/watch?v=...")

    # Özetle butonu
    if st.button("Özetle", type="primary"):
        if not video_url:
            st.warning("⚠️ Lütfen bir YouTube URL girin.")
        elif not is_valid_youtube_url(video_url):
            st.error("❌ Geçersiz YouTube URL formatı. Lütfen 'https://www.youtube.com/watch?v=...' formatında bir link girin.")
        else:
            try:
                # Yükleniyor animasyonu
                with st.spinner("🔄 Video bilgileri alınıyor ve özet oluşturuluyor... Lütfen bekleyin."):
                    start_time = time.time()
                    
                    # --- YouTube Bilgilerini Alma ---
                    logger.info(f"Video bilgileri alınıyor: {video_url}")
                    yt = YouTube(
                        video_url,
                        on_progress_callback=on_progress,
                        use_oauth=False,
                        allow_oauth_cache=True
                    )
                    
                    video_title = clean_text(yt.title, 100) or "Başlıksız Video"
                    video_description = clean_text(yt.description, 500) or ""
                    
                    logger.info(f"Video başlığı: {video_title}")
                    
                    # --- Transkripti Alma ---
                    logger.info("Transkript alınıyor...")
                    transcript = get_youtube_transcript(yt)
                    
                    # --- İçeriği Hazırlama ---
                    full_content = f"BAŞLIK: {video_title}\n\nAÇIKLAMA: {video_description}"
                    
                    if transcript:
                        full_content += f"\n\nTRANSKRIPT:\n{clean_text(transcript,max_length=500000)}"
                        logger.info(f"Transkript uzunluğu: {len(transcript)} karakter")
                    else:
                        logger.warning("Transkript bulunamadı. Sadece başlık ve açıklama özetlenecek.")
                        if not video_description:
                            st.error('❌ Video transkripti bulunamadı ve açıklaması boş. Bu video özetlenemiyor.')
                            st.info("💡 **Öneri:** Altyazılı bir video deneyin veya açıklaması dolu bir video seçin.")
                            st.stop()
                        else:
                            st.warning("⚠️ Video transkripti bulunamadı. Sadece başlık ve açıklama özetlenecek.")

                    # --- Özetleme İşlemi ---
                    logger.info("AI modeli ile özetleme başlatıldı")
                    prompt = generate_summary_prompt(full_content)
                    response = model.generate_content(prompt)
                    
                    
                    duration = time.time() - start_time
                    logger.info(f"Özetleme tamamlandı ({duration:.2f}s)")
                    
                    # --- Sonuçları Ekranda Gösterme ---
                    st.divider()
                    st.header(f"📄 {video_title}")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(yt.thumbnail_url, caption="Video Kapağı", use_container_width=True)
                        st.caption(f"⏱️ Süre: {yt.length // 60} dakika {yt.length % 60} saniye")
                        st.caption(f"👁️ Görüntülenme: {yt.views:,}")
                        st.caption(f"✅ Özetleme süresi: {duration:.2f} saniye")
                    
                    with col2:
                        st.subheader("📝 Video Özeti")
                        st.markdown(response.text)
                    
                    # Video linkini göster
                    st.divider()
                    st.markdown(f"🔗 [Videoyu YouTube'da İzle]({video_url})")

            except Exception as e:
                logger.error(f"Streamlit Özetleme Hatası: {str(e)}")
                st.error(f"❌ Video özetlenirken bir hata oluştu: {str(e)}")
                st.info("💡 **Olası Çözümler:**\n- Farklı bir video deneyin\n- URL'nin doğru olduğundan emin olun\n- Video gizli veya yaş kısıtlamalı olabilir")