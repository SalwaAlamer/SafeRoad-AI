# استيراد مكتبة OpenCV لمعالجة الصور
import cv2
# استيراد مكتبة Numpy للتعامل مع المصفوفات الحسابية للصور
import numpy as np


# 1. دالة تحسين الإضاءة الضعيفة (Enhance Low Light)
def enhance_low_light(image_rgb: np.ndarray, brightness: int = 28, clip_limit: float = 2.0) -> np.ndarray:
    """تطبيق تحسين خفيف للإضاءة قبل البدء في الرصد بالموديل."""
    
    # تحويل الصورة من نظام RGB إلى نظام LAB
    # نظام LAB يفصل الإضاءة (L) عن الألوان (A و B)، وهذا يسمح لنا بتعديل الإضاءة دون تخريب الألوان
    lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab) # فصل القنوات

    # استخدام تقنية CLAHE (تحسين التباين التكيفي المحدود)
    # وظيفتها توزيع الإضاءة بشكل متوازن في المناطق المظلمة دون جعل المناطق الفاتحة ساطعة جداً
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l_channel) # تطبيق التحسين على قناة الإضاءة فقط

    # إعادة دمج القنوات مرة أخرى (الإضاءة المحسنة + الألوان الأصلية)
    enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
    # تحويل الصورة مرة أخرى إلى نظام RGB العادي
    enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

    # إضافة لمسة أخيرة من السطوع (Brightness) وإرجاع الصورة النهائية
    return cv2.convertScaleAbs(enhanced_rgb, alpha=1.0, beta=brightness)


# 2. دالة تحديد بداية منطقة الاهتمام (ROI Start Y)
def roi_start_y(height: int, roi_ratio: float = 0.6) -> int:
    """حساب نقطة البداية (Y) لمنطقة التركيز على الطريق (النصف السفلي من الصورة)."""
    
    # التأكد أن النسبة المدخلة معقولة (بين 40% و 90% من طول الصورة السفلي)
    ratio = min(max(roi_ratio, 0.4), 0.9)
    # حساب الإحداثي Y الذي تبدأ عنده المنطقة (مثلاً لو الطول 1000 والنسبة 0.6، تبدأ المنطقة من 400)
    return int(height * (1.0 - ratio))


# 3. دالة التحقق من وجود الحفرة داخل منطقة الطريق (Is Box Inside ROI)
def is_box_inside_roi(box: tuple[int, int, int, int], image_height: int, roi_ratio: float = 0.6) -> bool:
    """التأكد من أن مركز الحفرة المرصودة يقع فعلياً داخل منطقة الطريق السفلية."""
    
    # استخراج إحداثيات المربع المرصود (y1 هي الحافة العليا و y2 هي السفلى)
    _, y1, _, y2 = box
    # حساب نقطة المنتصف للحفرة على المحور الرأسي
    center_y = (y1 + y2) / 2
    
    # إذا كان منتصف الحفرة أكبر من نقطة بداية الـ ROI، يعني أنها في النصف السفلي (على الطريق)
    # وبذلك نعتبرها "حفرة حقيقية" ونتجاهل أي حفر قد تظهر في السماء أو بعيداً عن الطريق
    return center_y >= roi_start_y(image_height, roi_ratio)