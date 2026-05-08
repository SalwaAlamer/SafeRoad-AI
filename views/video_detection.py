# استيراد مكتبة التعامل مع مسارات الملفات
from pathlib import Path
# استيراد مكتبة إنشاء ملفات مؤقتة لتخزين الفيديو أثناء المعالجة
import tempfile
# استيراد مكتبة الوقت لحساب سرعة المعالجة
import time

# استيراد مكتبة OpenCV الشهيرة للتعامل مع الصور والفيديوهات برمجياً
import cv2
# استيراد مكتبة Streamlit لبناء الواجهة
import streamlit as st

# استيراد دالة تشغيل التنبيه الصوتي عند وجود خطر
from utils.alerts import play_alert
# استيراد دالات تحميل الموديل ورصد الحفر
from utils.inference import detect_potholes, load_yolo_model
# استيراد دالة تسجيل النتائج (اللوق) في ملف خارجي (مثل الإكسيل)
from utils.logging import log_detection
# استيراد دالة تحسين الإضاءة الضعيفة للفيديوهات الليلية
from utils.preprocessing import enhance_low_light
# استيراد دالات حساب وتحليل مقاييس الخطورة للفيديو
from utils.severity import aggregate_video_metrics, calculate_metrics
# استيراد عناصر الواجهة: أزرار التحكم وكروت عرض النتائج
from utils.ui import detection_controls, metric_card


# تعريف الدالة الأساسية لعرض صفحة كشف الفيديو
def render_video_detection() -> None:
    st.title("Video Detection") # عنوان الصفحة
    st.caption("Process uploaded road videos...") # وصف قصير للميزة

    # تحميل موديل YOLOv8 في الذاكرة
    model = load_yolo_model()
    # جلب إعدادات المستخدم من القائمة الجانبية (وضع الليل، الثقة، منطقة التركيز)
    night_mode, confidence_threshold, roi_mode, roi_ratio = detection_controls("video")

    # إنشاء زر لرفع ملف الفيديو من الجهاز
    uploaded_video = st.file_uploader("Upload road video", type=["mp4", "avi", "mov", "mkv"])

    # إذا لم يتم رفع فيديو، توقف واعرض رسالة للمستخدم
    if not uploaded_video:
        st.info("Upload a video to begin processing.")
        return

    # إنشاء ملف مؤقت لحفظ الفيديو المرفوع لكي تتمكن مكتبة OpenCV من قراءته
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_video.name).suffix) as input_tmp:
        input_tmp.write(uploaded_video.read())
        input_path = Path(input_tmp.name)

    # تحديد مسار واسم ملف الفيديو الناتج (المعدل) الذي سيحمل المربعات الخضراء
    output_path = Path(tempfile.gettempdir()) / f"saferoad_annotated_{int(time.time())}.mp4"
    # فتح الفيديو باستخدام OpenCV للبدء في قراءة الإطارات
    cap = cv2.VideoCapture(str(input_path))

    # التأكد من أن الفيديو يفتح بشكل سليم
    if not cap.isOpened():
        st.error("The uploaded video could not be opened...")
        return

    # جلب معلومات الفيديو الأساسية: عدد الإطارات في الثانية، العرض، الطول، وإجمالي الإطارات
    fps = cap.get(cv2.CAP_PROP_FPS) or 20
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    # إعداد "كاتب الفيديو" (VideoWriter) لحفظ الفيديو الجديد بنفس المواصفات
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"), # ترميز الفيديو
        fps,
        (width, height),
    )

    # إنشاء شريط تقدم (Progress Bar) يظهر للمستخدم أثناء المعالجة
    progress = st.progress(0, text="Processing video frames...")
    frame_metrics = [] # قائمة لتخزين بيانات كل إطار
    total_start = time.perf_counter() # بدء حساب الوقت الإجمالي
    frame_index = 0 # عداد الإطارات

    # حلقة تكرارية (Loop) تمر على كل إطار في الفيديو
    while True:
        ok, frame_bgr = cap.read() # قراءة إطار واحد
        if not ok: # إذا انتهى الفيديو، اخرج من الحلقة
            break

        # تحويل ألوان الإطار من BGR (نظام OpenCV) إلى RGB (نظام الصور العادي)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        # إذا كان وضع الليل مفعلاً، قم بتحسين إضاءة الإطار قبل الرصد
        inference_input = enhance_low_light(frame_rgb) if night_mode else frame_rgb

        frame_start = time.perf_counter()
        # تنفيذ عملية الرصد (الذكاء الاصطناعي) على الإطار الحالي
        annotated_rgb, detections = detect_potholes(
            image_rgb=frame_rgb,
            model=model,
            confidence_threshold=confidence_threshold,
            roi_enabled=roi_mode,
            roi_ratio=roi_ratio,
            inference_image_rgb=inference_input,
        )
        # حساب وقت المعالجة لهذا الإطار وجمع البيانات
        inference_time = time.perf_counter() - frame_start
        frame_metrics.append(calculate_metrics(detections, frame_rgb.shape, inference_time=inference_time))

        # تحويل الإطار الموشم (الذي عليه مربعات) وحفظه في الفيديو الجديد
        writer.write(cv2.cvtColor(annotated_rgb, cv2.COLOR_RGB2BGR))
        frame_index += 1
        # تحديث شريط التقدم أمام المستخدم
        progress.progress(min(frame_index / total_frames, 1.0), text=f"Processing frame {frame_index}/{total_frames}")

    # إغلاق ملفات الفيديو المحملة والمكتوبة لتحرير الذاكرة
    cap.release()
    writer.release()
    progress.empty() # مسح شريط التقدم بعد الانتهاء

    # حساب إجمالي وقت المعالجة وتجميع كافة النتائج (المقاييس) للفيديو كاملاً
    processing_time = time.perf_counter() - total_start
    video_metrics = aggregate_video_metrics(frame_metrics, processing_time)

    # عرض الفيديو النهائي (الذي يحتوي على المربعات الخضراء) في الموقع
    st.subheader("Annotated Video")
    st.video(str(output_path))

    # عرض النتائج النهائية في 5 أعمدة مرتبة (العدد، الدقة، الخطورة، الوقت، الحالة)
    metric_cols = st.columns(5)
    metric_card(metric_cols[0], "Total Detections", video_metrics["total_detections"])
    metric_card(metric_cols[1], "Avg Confidence", f"{video_metrics['average_confidence']:.2f}")
    metric_card(metric_cols[2], "Max Severity", video_metrics["max_severity"])
    metric_card(metric_cols[3], "Processing Time", f"{video_metrics['processing_time']:.2f}s")
    metric_card(metric_cols[4], "Road Status", video_metrics["road_status"])

    # إذا تم رصد حفر، اظهر تنبيه أحمر وشغل صوت الإنذار
    if video_metrics["total_detections"] > 0:
        st.error("Hazard warning: valid pothole detections found after filtering.")
        play_alert()
    else:
        st.success("Road status: Safe based on the selected filtering controls.")

    # تسجيل بيانات العملية في السجل (مثل ملف الإكسيل)
    log_detection(uploaded_video.name, video_metrics)

    # إنشاء زر لتحميل الفيديو المعدل على جهاز الكمبيوتر
    with open(output_path, "rb") as video_file:
        st.download_button(
            "Download annotated video",
            data=video_file,
            file_name=f"annotated_{Path(uploaded_video.name).stem}.mp4",
            mime="video/mp4",
        )
