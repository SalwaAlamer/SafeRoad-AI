# استيراد مكتبة ستريمليت لبناء الواجهة
import streamlit as st

# تعريف الدالة التي ترسم صفحة "عن المشروع"
def render_about() -> None:
    # عنوان الصفحة الرئيسي (عن نظام SafeRoad AI)
    st.title("About SafeRoad AI")
    
    # نص تعريفي عام يشرح أن المشروع يركز على رصد الحفر في الصور والفيديوهات
    # ويوضح المميزات التقنية مثل فلترة الثقة وتحسين الإضاءة الضعيفة
    st.write(
        "SafeRoad AI is a graduation project focused on detecting potholes in road images "
        "and videos using YOLOv8. The application emphasizes practical reliability through "
        "confidence filtering, pothole-only detection, optional Road Focus ROI, and low-light "
        "enhancement."
    )

    # قسم "الأهداف" (Objective)
    st.markdown("### Objective")
    # شرح الهدف الأساسي: دعم مراقبة سلامة الطرق وتقديم مقاييس واضحة للعرض الأكاديمي
    st.write(
        "Support safer road monitoring by detecting visible pothole hazards and presenting "
        "clear metrics that can be demonstrated in an academic setting."
    )

    # قسم "التقنيات المستخدمة" (Technologies)
    st.markdown("### Technologies")
    # سرد لغات البرمجة والمكتبات والأدوات التي بنيتِ بها المشروع (بايثون، YOLOv8، إلخ)
    st.write("Python, Streamlit, YOLOv8 Ultralytics, OpenCV, Pandas, NumPy, and Google Colab training.")

    # قسم "العمل المستقبلي" (Future Work) - مهم جداً للمناقشة
    st.markdown("### Future Work")
    # توضيح الأفكار التي يمكن إضافتها مستقبلاً (مثل GPS حقيقي، دعم الكاميرا المباشرة، وتطبيق الجوال)
    st.write(
        "Future versions can add real GPS integration, live camera support, richer ROI controls, "
        "night-specific model training, mobile deployment, and map-based hazard reporting."
    )

    # قسم "المطور" (Developer)
    st.markdown("### Developer")
    # عرض أسماء المطورات (سلوى وريهام) داخل مربع أخضر جميل (st.success)
    st.success("Developed by Reham - Salwa - Mona - Basma - Afnan - Kholoud ")