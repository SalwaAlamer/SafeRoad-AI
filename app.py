import streamlit as st
# استيراد الدوال من المجلدات الفرعية
from utils.ui import apply_theme
from views.about import render_about
from views.home import render_home
from views.image_detection import render_image_detection
from views.model_performance import render_model_performance
from views.camera_detect import render_camera_detection

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="SafeRoad AI",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تطبيق الثيم (CSS)
try:
    apply_theme()
except:
    pass

# القائمة الجانبية
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2555/2555013.png", width=100) # أيقونة بسيطة
st.sidebar.markdown("## SafeRoad AI")
st.sidebar.caption("AI-powered pothole detection system")
st.sidebar.divider()

# التنقل بين الصفحات
page = st.sidebar.radio(
    "📍 Navigation",
    ["Home", "Image Detection", "Live Camera", "Model Performance", "About"],
)

# منطق عرض الصفحات
if page == "Home":
    render_home()
elif page == "Image Detection":
    render_image_detection()
elif page == "Live Camera":
    render_camera_detection()
elif page == "Model Performance":
    render_model_performance()
else:
    render_about()

# تذييل الصفحة الموحد
st.markdown("<br><br><hr><center style='color: #64748B;'>Graduation Project | Jazan University 2026</center>", unsafe_allow_html=True)


#streamlit run app.py

#  py -m streamlit run app.py