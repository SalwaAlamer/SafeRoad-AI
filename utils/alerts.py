from pathlib import Path
import time
import streamlit as st
import base64

# إعداد المسارات
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALERT_PATH = PROJECT_ROOT / "assets" / "alert.mp3"
ALERT_COOLDOWN_SECONDS = 5
ALERT_LAST_PLAYED_KEY = "alert_last_played_at"

def play_alert() -> None:
    """
    تشغيل التنبيه باستخدام HTML5 لتجنب أخطاء تكرار العناصر في Streamlit.
    """
    if not ALERT_PATH.exists():
        return

    now = time.time()
    last_played = st.session_state.get(ALERT_LAST_PLAYED_KEY, 0)
    
    if now - last_played < ALERT_COOLDOWN_SECONDS:
        return

    st.session_state[ALERT_LAST_PLAYED_KEY] = now

    # تحويل ملف الصوت إلى Base64 لتشغيله عبر HTML
    with open(ALERT_PATH, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        
    # إنشاء كود HTML لتشغيل الصوت تلقائياً بدون إظهار مشغل الموسيقى
    audio_html = f"""
        <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    
    # استخدام حاوية فارغة وتحديثها بكود الـ HTML
    placeholder = st.empty()
    placeholder.markdown(audio_html, unsafe_allow_html=True)
    
    # مسح الحاوية بعد فترة قصيرة لتهيئة الفريم القادم
    time.sleep(0.1)
    placeholder.empty()