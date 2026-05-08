# استيراد الأدوات اللازمة
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
import cv2
import numpy as np
import streamlit as st
import pandas as pd # أضفنا باندا للسجلات
from datetime import datetime # أضفنا الوقت والتاريخ

# استيراد دالات التأكد من منطقة الطريق
from utils.preprocessing import is_box_inside_roi, roi_start_y

# تحديد المسارات
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "MODELS" / "best.pt"
MODEL_PATHS = [MODEL_PATH]
POTHOLE_CLASS_NAME = "pothole"

@dataclass
class Detection:
    box: tuple[int, int, int, int]
    confidence: float
    class_name: str
    area_ratio: float

# --- 1. دالة تسجيل البيانات (الرابط مع صفحة الإحصائيات) ---
def log_detection(confidence, area_ratio):
    log_file = "detections_log.csv"
    
    # تحديد مستوى الخطورة بناءً على مساحة الحفرة في الصورة
    severity = "High" if area_ratio > 0.05 else "Medium" if area_ratio > 0.02 else "Low"
    
    new_data = {
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "confidence": [confidence],
        "severity": [severity]
    }
    new_df = pd.DataFrame(new_data)
    
    # حفظ في ملف CSV
    if not Path(log_file).exists():
        new_df.to_csv(log_file, index=False)
    else:
        new_df.to_csv(log_file, mode='a', header=False, index=False)

@lru_cache(maxsize=1)
def load_yolo_model() -> Any | None:
    model_path = next((path for path in MODEL_PATHS if path.exists()), None)
    if model_path is None:
        st.error(f"Model weight file not found at: {MODEL_PATH}")
        return None
    try:
        from ultralytics import YOLO
        return YOLO(str(model_path))
    except: return None

# --- 2. الدالة الأساسية المعدلة للرصد وتسجيل النتائج ---
def detect_potholes(image_rgb, model, confidence_threshold=0.20, **kwargs):
    if model is None: return image_rgb, []
    
    results = model.predict(source=image_rgb, conf=confidence_threshold, imgsz=640, verbose=False)
    
    annotated = image_rgb.copy()
    detections = []
    height, width = image_rgb.shape[:2]
    image_area = width * height

    for box_data in results[0].boxes:
        conf = float(box_data.conf[0])
        cls_id = int(box_data.cls[0])
        class_name = model.names.get(cls_id, str(cls_id)).lower()
        
        if class_name != POTHOLE_CLASS_NAME: continue

        x1, y1, x2, y2 = [int(v) for v in box_data.xyxy[0].tolist()]
        area_ratio = max((x2 - x1) * (y2 - y1), 0) / image_area
        
        # --- التعديل الجوهري: تسجيل الحفرة فور رصدها ---
        log_detection(conf, area_ratio) 
        
        det = Detection(box=(x1, y1, x2, y2), confidence=conf, class_name=class_name, area_ratio=area_ratio)
        detections.append(det)
        
        # رسم المربعات
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 220, 110), 3)
        cv2.putText(annotated, f"pothole {conf:.2f}", (x1, max(y1 - 10, 25)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 110), 2)

    return annotated, detections
