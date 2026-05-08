import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import time

# --- 1. إعدادات الصفحة والهوية ---
st.set_page_config(page_title="SafeRoad AI | Official Portal", layout="wide")

# --- 2. دالة تحميل الموديل (YOLOv8) ---
@st.cache_resource
def load_yolo_model():
    # البحث عن ملف الأوزان الذي تم تدريبه لمدة 37 ساعة
    search_paths = ['MODELS/best.pt', 'models/best.pt', 'best.pt']
    for path in search_paths:
        if os.path.exists(path):
            return YOLO(path)
    return None

model = load_yolo_model()

# --- 3. محرك التقارير الرسمي (Official PDF Engine) ---
def create_pdf_report(detections_count, image_path, severity="Medium"):
    pdf = FPDF()
    pdf.add_page()
    
    # الترويسة الرسمية للمملكة
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="KINGDOM OF SAUDI ARABIA", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 7, txt="Ministry of Transport and Logistic Services", ln=True, align='C')
    pdf.cell(200, 7, txt="SafeRoad AI: Infrastructure Monitoring Unit", ln=True, align='C')
    
    # خط فاصل ملون (أخضر سعودي)
    pdf.set_draw_color(0, 108, 53) 
    pdf.line(10, 35, 200, 35)
    pdf.ln(15)
    
    # تفاصيل التقرير الرقمية
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="OFFICIAL ROAD ANOMALY INSPECTION REPORT", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 8, txt=f"Report Reference: SR-JAZAN-{datetime.now().strftime('%Y%m%d')}", ln=0)
    pdf.cell(100, 8, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=1, align='R')
    pdf.cell(100, 8, txt=f"Time: {datetime.now().strftime('%H:%M:%S')}", ln=0)
    pdf.cell(100, 8, txt=f"Location: Jazan University Sector", ln=1, align='R')
    
    # حالة الخطورة
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Severity Status: ")
    if severity == "High":
        pdf.set_text_color(220, 20, 60) # أحمر للخطورة العالية
    pdf.cell(60, 10, txt=f"{severity} Priority", ln=1)
    pdf.set_text_color(0, 0, 0)
    
    # نص الخطاب الإداري
    pdf.set_font("Arial", '', 11)
    content = (f"Automated surveillance via YOLOv8 has identified {detections_count} anomalies. "
               "Technical analysis classifies this section as a priority for maintenance. "
               "Evidence photo is attached below for engineering review.")
    pdf.multi_cell(0, 8, txt=content)
    
    # إدراج صورة الحفرة المكتشفة
    pdf.ln(5)
    if os.path.exists(image_path):
        pdf.image(image_path, x=10, y=pdf.get_y(), w=170)
    
    # قسم التواقيع والختم
    pdf.set_y(250)
    pdf.line(10, 248, 200, 248)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 10, txt="Authorized Developer: Reham & Team", ln=0)
    pdf.cell(90, 10, txt="Official Ministry Stamp", ln=1, align='R')
    
    report_name = f"Official_SafeRoad_Report_{int(time.time())}.pdf"
    pdf.output(report_name)
    return report_name

# --- 4. واجهة الكاميرا الحية (Live Radar Section) ---
def render_camera_detection():
    st.markdown("<h1 style='text-align: center; color: #006C35;'>SA SafeRoad AI: DroidCam Live Radar</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Automated Road Health Monitoring System</p>", unsafe_allow_html=True)
    st.divider()

    if model is None:
        st.error("❌ Deep Learning Weights 'best.pt' not found in system paths!")
        return

    # إعدادات الاتصال (DroidCam)
    DROID_IP = "192.168.68.115" # تأكدي من تطابق الـ IP مع هاتفك
    camera_url = f"http://{DROID_IP}:4747/video"
    
    # الشريط الجانبي للمعلومات
    with st.sidebar:
        st.header("📡 Network Status")
        st.info(f"Target IP: {DROID_IP}")
        st.success("Protocol: HTTP Stream")
        if "total_detections" not in st.session_state:
            st.session_state.total_detections = 0
        st.metric("Total Potholes Detected", st.session_state.total_detections)

    run_scan = st.checkbox('🚀 Start Autonomous Surveillance Scan')
    FRAME_WINDOW = st.image([])

    if run_scan:
        cap = cv2.VideoCapture(camera_url)
        
        # تجربة المسار البديل إذا فشل الأول
        if not cap.isOpened():
            cap = cv2.VideoCapture(f"http://{DROID_IP}:4747/mjpegfeed")

        if not cap.isOpened():
            st.error("📡 Connection Failed. Check DroidCam App on your phone.")
        else:
            while run_scan:
                ret, frame = cap.read()
                if not ret: break

                # تشغيل الكشف (Inference)
                results = model.predict(frame, conf=0.5, verbose=False)
                res_plotted = results[0].plot() # رسم المربعات الملونة
                num_found = len(results[0].boxes)

                # عرض البث الحي
                FRAME_WINDOW.image(cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB))

                if num_found > 0:
                    st.session_state.total_detections += num_found
                    st.toast(f"🚨 ALERT: {num_found} Pothole(s) Identified!", icon="⚠️")
                    
                    # حفظ لقطة للتقرير الإداري
                    shot_path = "latest_detection.jpg"
                    cv2.imwrite(shot_path, res_plotted)
                    time.sleep(0.5) # تجنب تكرار التسجيل لنفس الحفرة سريعاً

            cap.release()

    # --- 5. قسم استخراج التقارير الرسمية ---
    if os.path.exists("latest_detection.jpg"):
        st.divider()
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("latest_detection.jpg", caption="Latest Visual Evidence")
        with col2:
            st.subheader("📋 Administrative Action")
            # تحديد الخطورة بناءً على العدد (كمثال منطقي)
            severity = "High" if st.session_state.total_detections > 3 else "Medium"
            
            if st.button("📑 Generate Official PDF Report"):
                with st.spinner("Compiling Ministry Report..."):
                    pdf_path = create_pdf_report(st.session_state.total_detections, "latest_detection.jpg", severity)
                    with open(pdf_path, "rb") as f:
                        st.download_button("📥 Download Official Report", f, file_name=pdf_path)
                    st.success("Report generated successfully.")

# --- تشغيل التطبيق ---
if __name__ == "__main__":
    # هذا الكود يمثل صفحة الكاميرا، ويمكن ربطه بـ Home عبر Sidebar Navigation
    render_camera_detection()