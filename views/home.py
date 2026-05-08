from pathlib import Path
import streamlit as st

def render_home() -> None:
    # 1. تخصيص التصميم للوضع الليلي الفخم (Deep Dark & Gold)
    st.markdown("""
        <style>
        /* ستايل قسم الترحيب الرئيسي */
        .home-hero {
            background: linear-gradient(135deg, #0a192f 0%, #020c1b 100%);
            padding: 60px 40px;
            border-radius: 25px;
            text-align: center;
            border: 1px solid rgba(100, 255, 218, 0.1);
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
        }
        
        /* إضافة تأثير ضوء خلفي خفيف */
        .home-hero::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,215,0,0.05) 0%, rgba(0,0,0,0) 70%);
            z-index: 0;
        }
        
        .home-hero * {
            position: relative;
            z-index: 1;
        }

        /* تصميم الكروت الزجاجية (Glassmorphism) */
        .feature-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            text-align: center;
            height: 250px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .feature-card:hover {
            transform: translateY(-10px);
            border-color: #FFD700;
            background: rgba(255, 215, 0, 0.02);
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.1);
        }
        .feature-card h3 {
            color: #FFD700; /* ذهبي */
            font-size: 19px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .feature-card p {
            color: #8892b0; /* أزرق رمادي ناعم */
            font-size: 14px;
            line-height: 1.6;
        }
        
        /* أيقونات الكروت */
        .card-icon {
            font-size: 45px;
            margin-bottom: 15px;
            color: #64ffda; /* فيروزي مضيء */
        }

        /* صندوق الرؤية */
        .vision-box {
            background: rgba(100, 255, 218, 0.03);
            border-left: 5px solid #64ffda;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. قسم البطل (Hero Section) ترحيب ملكي
    st.markdown("""
        <div class="home-hero">
            <div class="card-icon" style="font-size: 60px; color: #FFD700;">🛣️</div>
            <h1 style="color: #ccd6f6; margin: 10px 0; font-size: 42px; font-weight: 800;">SafeRoad AI</h1>
            <p style="color: #64ffda; font-size: 20px; font-weight: 500; letter-spacing: 1px;">
                Advanced AI Pothole Detection & Reporting System
            </p>
            <p style="color: #8892b0; max-width: 750px; margin: 20px auto; line-height: 1.7; font-size: 15px;">
                A premier graduation project utilizing state-of-the-art <b>Deep Learning (YOLOv8)</b> to monitor road health. 
                Our system provides high-speed detection, automated official reporting, and interactive performance analytics, 
                ensuring safer infrastructure and proactive maintenance in the Jazan region.
            </p>
            <hr style="width: 40%; margin: 25px auto; border-top: 1px solid rgba(100,255,218,0.1);">
            <p style="font-weight: bold; color: #ccd6f6; margin-bottom: 5px;">Distinguished Developers</p>
            <p style="font-size: 14px; color: #64ffda;">Salwa & Reham</p>
            <p style="font-size: 11px; color: #555;">College of Computer Science & IT | Jazan University 2026</p>
        </div>
    """, unsafe_allow_html=True)

    # 3. كروت المميزات (System Capabilities) بتصميم زجاجي
    st.markdown("<h3 style='color: #ccd6f6; text-align: center; margin-bottom: 30px;'>🌌 Core System Capabilities</h3>", unsafe_allow_html=True)
    cards = [
        ("👁️ Image Intelligence", "Upload road visuals for near-instant AI analysis, displaying precise red-box annotations and confidence scores."),
        ("🎥 Live Surveillance", "Process live camera feeds to detect hazards on the move, maintaining safe road environments in real-time."),
        ("📤 Official Reporting", "Generate academic and government-standard PDF reports, automatically addressed to the Ministry of Transport."),
        ("📊 Analytics Dashboard", "Explore interactive performance metrics, including Accuracy, Precision, Recall, and Daily Severity Trends.")
    ]

    cols = st.columns(4)
    for col, (title, body) in zip(cols, cards):
        # استخراج الأيقونة من العنوان
        icon, clean_title = title.split(' ', 1)
        with col:
            st.markdown(f"""
                <div class="feature-card">
                    <div class="card-icon">{icon}</div>
                    <h3>{clean_title}</h3>
                    <p>{body}</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 4. الرؤية ونطاق المشروع (Vision & Scope)
    col_vision, col_scope = st.columns([1, 1])
    
    with col_vision:
        st.markdown("""
            <div class="vision-box">
                <h3 style="margin-top:0; color: #64ffda;">SA Vision 2030 </h3>
                <p style="color: #8892b0; font-size: 14px;">
                SafeRoad AI proudly supports <b>Saudi Vision 2030</b> by introducing AI-driven 
                digital transformation to infrastructure monitoring, aiming to reduce maintenance 
                costs and improve public road safety standard.</p>
            </div>
        """, unsafe_allow_html=True)

    with col_scope:
        st.markdown("<h3 style='color: #ccd6f6; margin-top:10px;'>🎯 Project Scope</h3>", unsafe_allow_html=True)
        st.markdown("""
            <p style="color: #8892b0; font-size: 14px; line-height: 1.6;">
            Designed for local infrastructure deployment, utilizing a custom 
            <b style="color:#64ffda;">YOLOv8 Nano</b> model optimized for CPU inference. 
            The solution ensures data privacy through local logging while providing 
            comprehensive historical data database.</p>
        """, unsafe_allow_html=True)

    # 5. رسالة تذكير بأسلوب ليلي
    st.info(
        "**System Note:** Currently monitoring road health in Jazan City. Data is logged locally for security."
    )