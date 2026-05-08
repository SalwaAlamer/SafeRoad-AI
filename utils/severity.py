# استيراد الأدوات اللازمة لتعريف قوالب البيانات والتعامل مع القوائم
from dataclasses import dataclass
from typing import Iterable

# تعريف "قالب بيانات" (Dataclass) لتنظيم نتائج الحسابات في مكان واحد
@dataclass
class DetectionMetrics:
    pothole_count: int        # عدد الحفر
    average_confidence: float  # متوسط الثقة
    severity_label: str       # نص مستوى الخطر (Low, Medium, High)
    severity_percent: float   # نسبة الخطر المئوية
    road_status: str          # حالة الطريق (Safe, Hazard)
    inference_time: float = 0.0 # وقت المعالجة بالثواني


# الدالة الأساسية لحساب المقاييس بناءً على الحفر المكتشفة في صورة واحدة
def calculate_metrics(detections: Iterable, image_shape: tuple[int, ...], inference_time: float = 0.0) -> DetectionMetrics:
    """حساب مستوى الخطورة بناءً على الحفر المؤكدة فقط."""
    
    valid = list(detections) # تحويل المكتشفات إلى قائمة
    count = len(valid)       # حساب عددها
    
    # إذا لم توجد حفر، ارجع تقرير "طريق آمن" ببيانات صفرية
    if count == 0:
        return DetectionMetrics(0, 0.0, "Low", 0.0, "Safe", inference_time)

    # حساب متوسط ثقة الموديل لجميع الحفر في الصورة
    average_confidence = sum(item.confidence for item in valid) / count
    # تحديد أكبر حفرة من حيث المساحة بالنسبة للصورة (area_ratio)
    largest_area = max(item.area_ratio for item in valid)

    # --- معادلة حساب درجة الخطورة (Severity Scoring) ---
    # 1. درجة العدد: كلما زاد العدد زاد الخطر (بحد أقصى 5 حفر تعطي 40 نقطة)
    count_score = min(count / 5, 1.0) * 40
    # 2. درجة الثقة: دقة تأكد الموديل تساهم بـ 30 نقطة
    confidence_score = average_confidence * 30
    # 3. درجة المساحة: الحفر الكبيرة تساهم بـ 30 نقطة (تعتبر كبيرة إذا غطت 15% من الصورة)
    area_score = min(largest_area / 0.15, 1.0) * 30
    
    # جمع الدرجات للحصول على نسبة مئوية إجمالية للخطر (لا تتعدى 100%)
    severity_percent = min(count_score + confidence_score + area_score, 100)

    # تحويل النسبة المئوية إلى "ملصق" أو نص (High, Medium, Low)
    if severity_percent >= 70:
        severity_label = "High"
    elif severity_percent >= 40:
        severity_label = "Medium"
    else:
        severity_label = "Low"

    # إرجاع كافة النتائج داخل القالب الذي عرفناه في البداية
    return DetectionMetrics(
        pothole_count=count,
        average_confidence=average_confidence,
        severity_label=severity_label,
        severity_percent=severity_percent,
        road_status="Hazard",
        inference_time=inference_time,
    )


# دالة تجميع النتائج لملف فيديو كامل (لأن الفيديو يتكون من مئات الإطارات)
def aggregate_video_metrics(frame_metrics: list[DetectionMetrics], processing_time: float) -> dict:
    """تجميع مقاييس الإطارات الفردية للخروج بملخص نهائي للفيديو."""
    
    # إجمالي عدد الحفر المرصودة في كل ثواني الفيديو
    total_detections = sum(metric.pothole_count for metric in frame_metrics)
    
    # جمع قيم الثقة فقط من الإطارات التي احتوت فعلياً على حفر
    confidence_values = [
        metric.average_confidence
        for metric in frame_metrics
        if metric.pothole_count > 0 and metric.average_confidence > 0
    ]
    average_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
    
    # إيجاد أعلى نسبة خطر تم تسجيلها في أي إطار من إطارات الفيديو
    max_percent = max((metric.severity_percent for metric in frame_metrics), default=0.0)
    # تحويل أعلى نسبة إلى نص (Low, Medium, High)
    max_severity = _severity_from_percent(max_percent)

    # إرجاع قاموس (Dictionary) يحتوي على التقرير النهائي للفيديو
    return {
        "total_detections": total_detections,
        "average_confidence": average_confidence,
        "max_severity": max_severity,
        "severity_percent": max_percent,
        "road_status": "Hazard" if total_detections > 0 else "Safe",
        "processing_time": processing_time,
        "pothole_count": total_detections,
        "severity_label": max_severity,
    }


# دالة مساعدة لتحويل الرقم المئوي إلى وصف نصي لمستوى الخطر
def _severity_from_percent(percent: float) -> str:
    if percent >= 70:
        return "High"
    if percent >= 40:
        return "Medium"
    return "Low"



    
