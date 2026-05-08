import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
from utils.evaluation import compute_model_evaluation, load_evaluation_metrics

# --- إعداد المسارات الموحدة لمشروع SafeRoad AI ---
BASE_DIR = Path(__file__).resolve().parent.parent
# التأكد من أن المسار يشير إلى الملف الذي يتم تحديثه بواسطة الكاميرا الحية
# --- إعداد المسارات الموحدة لمشروع SafeRoad AI ---
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "data" / "detections_log.csv"
ACTIVITY_COLUMNS = ["timestamp", "confidence", "severity", "latitude", "longitude"]

def render_model_performance():
    # ستايل CSS المطور لإضافة الـ Tooltips
    st.markdown("""
        <style>
        .metric-card {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            position: relative;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            cursor: help;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #FFD700;
        }
        .metric-card .tooltiptext {
            visibility: hidden;
            width: 180px;
            background-color: #1a1a1a;
            color: #FFD700;
            text-align: center;
            border: 1px solid #FFD700;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 110%;
            left: 50%;
            margin-left: -90px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 11px;
            line-height: 1.4;
        }
        .metric-card:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        .metric-value { font-size: 20px; font-weight: bold; color: #FFD700; margin: 0; }
        .metric-label { font-size: 11px; color: #8b949e; margin: 0; text-transform: uppercase; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; color: #FFD700;'>System Performance Analytics</h2>", unsafe_allow_html=True)
    st.divider()

    # تحديث البيانات تلقائياً عند الدخول للصفحة لضمان ظهور رصد الكاميرا الجديد
    st.cache_data.clear()

    # قراءة البيانات من ملف السجل الموحد (الذي تشارك فيه الكاميرا الحية)
    df = pd.DataFrame(columns=ACTIVITY_COLUMNS)
    if LOG_FILE.exists():
        try:
            df = pd.read_csv(LOG_FILE)
            # التأكد من معالجة التواريخ لتمثيل الرصد المباشر
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
            df = df.dropna(subset=['timestamp', 'confidence', 'severity'])
            df['date_only'] = df['timestamp'].dt.date
        except Exception as e:
            st.error(f"Error loading logs: {e}")

    evaluation_metrics = load_evaluation_metrics()
    
    # --- حساب المقاييس لتشمل رصد الكاميرا ---
    m_cols = st.columns(7)
    
    last_24_hours = datetime.now() - timedelta(hours=24)
    # حساب عدد الحفر المكتشفة اليوم (بما فيها رصد الكاميرا الأخير)
    today_count = len(df[df['timestamp'] >= last_24_hours]) if not df.empty else 0
    avg_confidence = f"{(df['confidence'].mean()*100):.1f}%" if not df.empty else "0.0%"
    
    accuracy = _format_metric(evaluation_metrics, "accuracy")
    precision = _format_metric(evaluation_metrics, "precision")
    recall = _format_metric(evaluation_metrics, "recall")
    f1 = _format_metric(evaluation_metrics, "f1")

    metrics_info = [
        ("Total Potholes", len(df), "Total detections from both Images and Live Camera."),
        ("Avg Confidence", avg_confidence, "Average AI certainty across all scan modes."),
        ("Accuracy", accuracy, "Overall model accuracy (TP+TN)/(Total)"),
        ("Precision", precision, "Model's ability to avoid False Positives."),
        ("Recall", recall, "Model's ability to capture all existing potholes."),
        ("F1-Score", f1, "Harmonic mean of Precision and Recall."),
        ("Today's Live", today_count, f"Detections recorded since {last_24_hours.strftime('%I:%M %p')}")
    ]

    for i, (label, value, formula) in enumerate(metrics_info):
        with m_cols[i]:
            st.markdown(f"""
                <div class="metric-card">
                    <span class="tooltiptext">{formula}</span>
                    <p class="metric-label">{label}</p>
                    <p class="metric-value">{value}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- الرسوم البيانية المرتبطة بالوقت الحقيقي ---
    col_graph, col_table = st.columns([1.6, 1]) 

    with col_graph:
        st.markdown("#### 📈 Severity Trends (Including Live Scans)")
        if df.empty:
            st.info("No detection activity recorded yet.")
        else:
            # تجميع البيانات حسب اليوم والخطورة (Severity)
            daily_counts = df.groupby(['date_only', 'severity'], as_index=False).size()
            daily_counts = daily_counts.rename(columns={'size': 'Count'})
            fig = px.bar(
                daily_counts, x='date_only', y='Count', color='severity',
                barmode='group',
                color_discrete_map={'High': '#EF4444', 'Medium': '#FACC15', 'Low': '#4ADE80'},
                template="plotly_dark", height=380 
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("#### 📄 Global Detection Log")
        if df.empty:
            st.info("Logs are empty.")
        else:
            # عرض السجلات مرتبة من الأحدث (الرصد الحي الأخير يظهر أولاً)
            st.dataframe(
                df[['timestamp', 'confidence', 'severity', 'latitude', 'longitude']]
                .sort_values(by='timestamp', ascending=False),
                height=380, use_container_width=True
            )

def _format_metric(metrics: dict | None, key: str) -> str:
    if not metrics or key not in metrics or pd.isna(metrics[key]):
        return "N/A"
    return f"{float(metrics[key]) * 100:.1f}%"