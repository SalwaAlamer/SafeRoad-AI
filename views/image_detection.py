import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from pathlib import Path
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import geocoder
import os
from utils.alerts import play_alert
from utils.logging import append_detection_log

# --- 1. Paths & Model Loading ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "MODELS" / "best.pt"

@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        st.error(f"Model weight file not found at: {MODEL_PATH}")
        return None
    return YOLO(str(MODEL_PATH))

model = load_model()

# --- 2. Location Function (Default: Jazan) ---
def get_location():
    try:
        g = geocoder.ip("me")
        if g.latlng:
            return g.latlng[0], g.latlng[1], f"{g.city}, {g.country}"
        return 16.8892, 42.5511, "Jazan, SA"
    except:
        return 16.8892, 42.5511, "Jazan, SA"

# --- 3. Official English PDF Report ---
def create_pdf(lat, lon, city, h, m, l, table_data, analyzed_img):
    pdf = FPDF()
    pdf.add_page()
    
    # Save the analyzed image temporarily
    temp_img_path = "detected_pothole_temp.jpg"
    Image.fromarray(analyzed_img).save(temp_img_path)

    # Report Header
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, "Official Road Maintenance Report", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, "Kingdom of Saudi Arabia", ln=True, align='R')
    pdf.cell(0, 8, "Ministry of Transport and Logistic Services", ln=True, align='R')
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='R')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "To: Road Maintenance Department", ln=True, align='L')
    
    # Body Text
    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    body = (f"This is an automated inspection report for road damages identified in {city}. "
            "The AI system has detected structural defects (Potholes) that may impact public safety. "
            "Current Status: Citizens are safe, but immediate maintenance intervention is required.")
    pdf.multi_cell(0, 10, body, align='L')
    
    # Insert Detection Image
    pdf.ln(5)
    pdf.cell(0, 10, "Evidence Image (AI Analysis):", ln=True, align='L')
    pdf.image(temp_img_path, x=30, w=150)
    
    # Data Summary
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Detection Summary: High: {h}, Medium: {m}, Low: {l}", ln=True)
    pdf.cell(0, 10, f"GPS Coordinates: {lat}, {lon}", ln=True)
    
    # Footer & Signature
    pdf.ln(20)
    pdf.cell(0, 10, "Best Regards,", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(0, 10, "Authorized Signature: ...........................", ln=True, align='L')
    pdf.cell(0, 10, "Official Department Stamp", ln=True, align='L')

    file_name = "Official_Road_Report.pdf"
    pdf.output(file_name)
    
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)
    return file_name

# --- 4. Streamlit UI ---
def render_image_detection():
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>🛣️ Smart Road Inspection System</h2>", unsafe_allow_html=True)
    st.divider()

    if model is None:
        return

    uploaded = st.file_uploader("Upload road image", type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        img_array = np.array(image)

        col1, col2 = st.columns([1.3, 1]) 

        with col1:
            st.markdown("#### 📸 Detection View")
            analyze_btn = st.button("🚀 Analyze Road Condition", use_container_width=True)
            image_placeholder = st.empty()
            image_placeholder.image(image, caption="Original Image", width=500)
            
            # Map under the image
            if "location_info" in st.session_state and st.session_state.location_info[0] is not None:
                lat, lon, city = st.session_state.location_info
                st.markdown(f"**📍 Location:** {city}")
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12, use_container_width=True)

        if analyze_btn:
            lat, lon, city = get_location()
            st.session_state.location_info = (lat, lon, city)
            
            # Run YOLO Model
            results = model(img_array)
            res_plotted = img_array.copy()
            table_records = []
            
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                sev = "High" if conf > 0.75 else "Medium" if conf > 0.5 else "Low"
                table_records.append({"confidence": conf * 100, "severity": sev})
                
                # Draw Red Bounding Boxes
                cv2.rectangle(res_plotted, (x1, y1), (x2, y2), (255, 0, 0), 4)
                cv2.putText(res_plotted, f"Pothole {conf:.2f}", (x1, y1 - 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 3)

            st.session_state.detected_image = res_plotted
            st.session_state.detection_details = table_records
            st.session_state.play_detection_alert = len(table_records) > 0
            if table_records:
                for record in table_records:
                    append_detection_log(record["confidence"] / 100, record["severity"], lat, lon)
                st.cache_data.clear()
            st.rerun()

        if st.session_state.get("detected_image") is not None:
            image_placeholder.image(st.session_state.detected_image, caption="AI Analysis Result", width=500)
            
            table_records = st.session_state.detection_details
            if st.session_state.pop("play_detection_alert", False):
                play_alert()
            h = len([r for r in table_records if r['severity'] == "High"])
            m = len([r for r in table_records if r['severity'] == "Medium"])
            l = len([r for r in table_records if r['severity'] == "Low"])

            with col2:
                st.markdown("#### 📋 Official Report")
                st.warning("⚠️ **Road damage detected!**")
                st.info("📢 **An automated report is being sent to authorities.**")
                
                # Download Button right after the message
                lat, lon, city = st.session_state.location_info
                pdf_file = create_pdf(lat, lon, city, h, m, l, table_records, st.session_state.detected_image)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download Official PDF Report", f, file_name="Road_Analysis_Report.pdf", use_container_width=True)
                
                st.divider()

                # Severity Summary Cards
                st.markdown(f"""
                <div style="background-color: #0d1117; padding: 15px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 20px;">
                    <div style="background: rgba(239, 68, 68, 0.15); border-left: 5px solid #EF4444; padding: 10px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between;">
                        <span style="color: #EF4444; font-weight: bold;">🔴 HIGH SEVERITY</span>
                        <span style="color: white; font-weight: bold;">{h}</span>
                    </div>
                    <div style="background: rgba(250, 204, 21, 0.15); border-left: 5px solid #FACC15; padding: 10px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between;">
                        <span style="color: #FACC15; font-weight: bold;">🟡 MEDIUM SEVERITY</span>
                        <span style="color: white; font-weight: bold;">{m}</span>
                    </div>
                    <div style="background: rgba(74, 222, 128, 0.15); border-left: 5px solid #4ADE80; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between;">
                        <span style="color: #4ADE80; font-weight: bold;">🟢 LOW SEVERITY</span>
                        <span style="color: white; font-weight: bold;">{l}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Technical Table
                st.markdown("#### 🔍 Technical Details")
                df_display = pd.DataFrame(table_records)
                df_display.index += 1 
                df_display.columns = ['Confidence (%)', 'Severity Level']
                st.dataframe(df_display.style.format({'Confidence (%)': '{:.2f}%'}), use_container_width=True)

if __name__ == "__main__":
    render_image_detection()
