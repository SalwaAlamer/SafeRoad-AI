# استيراد مكتبة ستريمليت لبناء الواجهة
import streamlit as st
# استيراد Any للسماح باستقبال أي نوع من البيانات (نصوص أو أرقام)
from typing import Any

# دالة تطبيق "الثيم" أو التنسيق البصري للموقع
def apply_theme() -> None:
    # استخدام st.markdown مع HTML/CSS لتغيير شكل الموقع الافتراضي
    st.markdown(
        """
        <style>
            /* تغيير خلفية الموقع للون الداكن ولون النص للأبيض المائل للزرقة */
            .stApp { background: #0f1115; color: #f5f7fa; }
            
            /* تغيير لون خلفية القائمة الجانبية (السايد بار) للون أغمق */
            section[data-testid="stSidebar"] { background: #151922; }
            
            /* تصميم "كارت" عرض البيانات (المربع الذي يحتوي على النتائج) */
            .metric-card {
                background: #181d27; /* لون خلفية الكرت */
                border: 1px solid #2a3140; /* إطار نحيف حول الكرت */
                border-radius: 10px; /* جعل زوايا المربع منحنية */
                padding: 10px; /* مسافة داخلية بين النص والإطار */
                text-align: center; /* توسيط النص */
                margin-bottom: 10px; /* مسافة تحت الكرت */
            }
            
            /* تنسيق النص العلوي (العنوان) داخل الكرت */
            .metric-card .label { color: #f0c96a; font-size: 0.8rem; margin-bottom: 2px; }
            
            /* تنسيق القيمة الرقمية الكبيرة داخل الكرت */
            .metric-card .value { font-size: 1.1rem; font-weight: 700; color: #ffffff; }
            
            /* إضافة انحناء لزوايا الصور المعروضة في الموقع لتبدو أجمل */
            [data-testid="stImage"] img { border-radius: 10px; }
        </style>
        """,
        # تسمح للموقع بتنفيذ أكواد HTML و CSS مخصصة
        unsafe_allow_html=True,
    )

# دالة رسم الكرت (المربع) واستقبال البيانات لعرضها بداخله
def metric_card(column, label: str, value: Any) -> None:
    # نقوم بحقن كود HTML داخل العمود المحدد لعرض الكرت بالتنسيق الذي صممناه فوق
    column.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# دالة التحكم في إعدادات الرصد (مثل نسبة الثقة ووضع الليل)
def detection_controls(key_prefix: str) -> tuple[bool, float, bool, float]:
    # قمنا بحذف أشرطة التمرير (Sliders) لجعل الواجهة نظيفة
    # ورجعنا قيم ثابتة برمجياً:
    # False: وضع الليل مغلق افتراضياً
    # 0.25: نسبة الثقة (Confidence Threshold) مثبتة على 25%
    # False: منطقة التركيز (ROI) مغلقة
    # 0.60: نسبة منطقة التركيز الافتراضية
    return False, 0.25, False, 0.60