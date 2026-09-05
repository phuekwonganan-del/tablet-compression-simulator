"""
Pharmaceutical Tablet Compression Simulator
Main App v1.0
Author: Tok
Run: streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np
import sys
import os
import time

sys.path.append(os.path.dirname(__file__))

from mainproject_physicc_engine import simulate, EXCIPIENTS
from machinemodule import simulate_single_punch, simulate_rotary
from exipient_database import EXCIPIENT_EXTENDED, print_excipient_profile
from defect_predictor import full_defect_analysis, predict_capping
from defect_predictor import predict_lamination, predict_sticking
from defect_predictor import predict_twinning, risk_level

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Tablet Compression Simulator",
    page_icon="/",
    layout="wide"
)

# ============================================================
# MATPLOTLIB — NASA THEME
# ============================================================

NASA = {
    "bg":        "#0B0C10",
    "panel":     "#1F2833",
    "accent":    "#45A29E",
    "highlight": "#66FCF1",
    "text":      "#C5C6C7",
    "pass":      "#4CAF50",
    "fail":      "#FF5722",
}

plt.rcParams.update({
    "figure.facecolor":  NASA["bg"],
    "axes.facecolor":    NASA["panel"],
    "axes.edgecolor":    NASA["accent"],
    "axes.labelcolor":   NASA["text"],
    "axes.titlecolor":   NASA["highlight"],
    "xtick.color":       NASA["text"],
    "ytick.color":       NASA["text"],
    "text.color":        NASA["text"],
    "grid.color":        "#45A29E40",
    "font.family":       "monospace",
    "legend.facecolor":  NASA["panel"],
    "legend.edgecolor":  NASA["accent"],
})

# ============================================================
# NASA-FEEL THEME
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

/* ===== GLOBAL ===== */
html, body, [class*="css"], .stMarkdown, p, span, label, li {
    color: #C5C6C7;
    font-family: 'Rajdhani', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 20% 10%, #1F283340 0%, transparent 45%),
        radial-gradient(circle at 85% 85%, #45A29E15 0%, transparent 40%),
        #0B0C10;
}

.block-container { padding-top: 2.5rem; }

/* ===== TYPOGRAPHY ===== */
h1 {
    color: #66FCF1 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 2.6rem !important;
    letter-spacing: 0.35rem !important;
    text-transform: uppercase;
    text-shadow: 0 0 24px rgba(102, 252, 241, 0.25);
    border-bottom: 1px solid #45A29E;
    padding-bottom: 14px;
    margin-bottom: 4px;
}

h2, h3, h4 {
    color: #45A29E !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.14rem !important;
    text-transform: uppercase;
}

/* section subheaders get a faint rule */
[data-testid="stHeading"] {
    border-left: 3px solid #45A29E;
    padding-left: 12px;
    margin-top: 8px;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: #1F2833;
    border-right: 1px solid #45A29E;
}
[data-testid="stSidebar"] * { color: #C5C6C7 !important; }
[data-testid="stSidebar"] [data-testid="stHeading"] {
    border-left: none;
    padding-left: 0;
    border-bottom: 1px solid #45A29E40;
    padding-bottom: 8px;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    background: #1F2833;
    border-radius: 4px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #45A29E30;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #C5C6C7;
    border-radius: 3px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 0.1rem;
    text-transform: uppercase;
    padding: 8px 18px;
    border: none;
    transition: all 0.15s;
}
.stTabs [aria-selected="true"] {
    background: #0B0C10 !important;
    color: #66FCF1 !important;
    box-shadow: inset 0 -2px 0 #45A29E;
}
.stTabs [data-baseweb="tab"]:hover { color: #66FCF1; }

/* ===== METRICS ===== */
[data-testid="stMetric"] {
    background: #1F2833;
    border: 1px solid #45A29E30;
    border-left: 3px solid #45A29E;
    border-radius: 4px;
    padding: 14px 16px;
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
    color: #45A29E !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.12rem;
}
[data-testid="stMetricValue"] {
    color: #66FCF1 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.6rem !important;
}
[data-testid="stMetricDelta"] { font-family: 'Share Tech Mono', monospace !important; }

/* ===== BUTTONS (outline + glow) ===== */
.stButton > button {
    background: transparent;
    color: #66FCF1;
    border: 1px solid #45A29E;
    border-radius: 3px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.15rem;
    text-transform: uppercase;
    padding: 8px 26px;
    transition: all 0.18s;
}
.stButton > button:hover {
    background: #45A29E1A;
    border-color: #66FCF1;
    color: #66FCF1;
    box-shadow: 0 0 16px rgba(102, 252, 241, 0.35);
}

/* ===== INPUTS ===== */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background: #66FCF1 !important; }
[data-testid="stSlider"] [data-testid="stThumbValue"],
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #66FCF1 !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
    background: #1F2833 !important;
    border: 1px solid #45A29E !important;
    color: #C5C6C7 !important;
    border-radius: 3px;
}
[data-testid="stRadio"] label { color: #C5C6C7 !important; font-family: 'Rajdhani', sans-serif !important; }

/* ===== ALERT CARDS ===== */
[data-testid="stSuccess"], [data-testid="stError"], [data-testid="stInfo"], [data-testid="stWarning"] {
    background: #1F2833;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
}
[data-testid="stSuccess"] { border-left: 3px solid #4CAF50; color: #4CAF50 !important; }
[data-testid="stError"]   { border-left: 3px solid #FF5722; color: #FF5722 !important; }
[data-testid="stWarning"] { border-left: 3px solid #FF5722; color: #FF5722 !important; }
[data-testid="stInfo"]    { border-left: 3px solid #45A29E; color: #C5C6C7 !important; }

/* ===== MISC ===== */
hr { border-color: #45A29E30 !important; }
[data-testid="stCaptionContainer"], .stCaption, [data-testid="stCaptionContainer"] * {
    color: #45A29E !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1rem;
}
[data-testid="stImage"], [data-testid="stImage"] img,
.stPlotlyChart, [data-testid="stPyplotChart"] {
    border: 1px solid #45A29E30;
    border-radius: 4px;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0B0C10; }
::-webkit-scrollbar-thumb { background: #45A29E; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #66FCF1; }

/* ===== BADGES ===== */
.nasa-badge {
    display: inline-block;
    background: #45A29E1A;
    border: 1px solid #45A29E;
    border-radius: 3px;
    padding: 3px 12px;
    margin: 2px 6px 2px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    color: #45A29E;
    text-transform: uppercase;
    letter-spacing: 0.18rem;
}
.nasa-rule {
    height: 1px;
    background: linear-gradient(90deg, #45A29E 0%, transparent 80%);
    margin: 6px 0 18px 0;
}
.nasa-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #45A29E;
    letter-spacing: 0.2rem;
}

</style>
""", unsafe_allow_html=True)


def section_rule():
    st.markdown('<div class="nasa-rule"></div>', unsafe_allow_html=True)


st.markdown('<h1>Tablet Compression Simulator</h1>', unsafe_allow_html=True)

col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
with col_t1:
    st.markdown(
        '<span class="nasa-badge">QbD Framework</span>'
        '<span class="nasa-badge">Physics Engine v1.0</span>'
        '<span class="nasa-badge">Author&nbsp;/&nbsp;Tok</span>',
        unsafe_allow_html=True,
    )
with col_t2:
    st.markdown('<span class="nasa-badge">Thammasat University</span>', unsafe_allow_html=True)
with col_t3:
    st.markdown('<span class="nasa-badge">Pharmacy Year 4</span>', unsafe_allow_html=True)

section_rule()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Parameters")
st.sidebar.markdown('<span class="nasa-sub">// INPUT VECTOR</span>', unsafe_allow_html=True)

excipient = st.sidebar.selectbox(
    "Excipient",
    list(EXCIPIENT_EXTENDED.keys())
)

pressure = st.sidebar.slider(
    "Compression Pressure (MPa)",
    min_value=10,
    max_value=300,
    value=150,
    step=10
)

force_kN = st.sidebar.slider(
    "Compression Force (kN)",
    min_value=1.0,
    max_value=100.0,
    value=10.0,
    step=1.0
)

speed = st.sidebar.slider(
    "Speed (rpm)",
    min_value=5,
    max_value=60,
    value=30,
    step=5
)

temperature = st.sidebar.slider(
    "Temperature (°C)",
    min_value=15,
    max_value=40,
    value=25,
    step=1
)

machine_type = st.sidebar.radio(
    "Machine Type",
    ["single", "rotary"]
)

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Physics Engine",
    "Machine Simulation",
    "Excipient Profile",
    "Defect Predictor",
    "Animation",
    "2D Diagram"
])

# ============================================================
# TAB 1 — PHYSICS ENGINE
# ============================================================

with tab1:
    st.subheader("Physics Engine — Heckel + Ryshkewitch + Fell-Newton")
    section_rule()

    result = simulate(excipient, pressure)
    
    if result:
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Relative Density", f"{result['density']:.4f}")
        col2.metric("Porosity", f"{result['porosity']:.4f}")
        col3.metric("Tensile Strength", f"{result['tensile']:.2f} MPa")
        col4.metric("Hardness", f"{result['hardness']:.2f} N")
        
        # QC Result
        if "✅" in result['qc']:
            st.success(f"QC Result: {result['qc']}")
        else:
            st.error(f"QC Result: {result['qc']}")
        
        st.divider()
        
        # Plot Hardness vs Pressure
        st.subheader("Hardness vs Pressure Curve")
        
        pressures = list(range(10, 310, 10))
        hardnesses = []
        
        for p in pressures:
            r = simulate(excipient, p)
            if r:
                hardnesses.append(r['hardness'])
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(pressures, hardnesses,
                color=NASA["highlight"], linewidth=2, label='Hardness')
        ax.axhline(y=40,  color=NASA["pass"], linestyle='--',
                   alpha=0.7, label='USP min (40 N)')
        ax.axhline(y=200, color=NASA["fail"],   linestyle='--',
                   alpha=0.7, label='USP max (200 N)')
        ax.axvline(x=pressure, color=NASA["accent"], linestyle='-',
                   alpha=0.9, label=f'Current ({pressure} MPa)')
        ax.fill_between(pressures, 40, 200, alpha=0.08, color=NASA["accent"])
        ax.set_xlabel("Pressure (MPa)")
        ax.set_ylabel("Hardness (N)")
        ax.set_title(f"Hardness vs Pressure — {excipient}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        plt.close()

# ============================================================
# TAB 2 — MACHINE SIMULATION
# ============================================================

with tab2:
    st.subheader("Machine Simulation")
    section_rule()

    if machine_type == "single":
        machine_result = simulate_single_punch(
            excipient, force_kN, speed
        )
    else:
        machine_result = simulate_rotary(
            excipient, force_kN, speed
        )
    
    if machine_result:
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Hardness (adjusted)", 
                    f"{machine_result['hardness_adjusted']:.2f} N")
        col2.metric("Uniformity (CV%)", 
                    f"{machine_result['cv_percent']:.1f} %")
        col3.metric("Throughput", 
                    f"{machine_result['throughput']} tab/min")
        col4.metric("Dwell Time", 
                    f"{machine_result['dwell_time']:.1f} ms")
        
        if "✅" in machine_result['qc']:
            st.success(f"QC: {machine_result['qc']}")
        else:
            st.error(f"QC: {machine_result['qc']}")

# ============================================================
# TAB 3 — EXCIPIENT PROFILE
# ============================================================

with tab3:
    st.subheader(f"Excipient Profile: {excipient}")
    section_rule()

    if excipient in EXCIPIENT_EXTENDED:
        exc = EXCIPIENT_EXTENDED[excipient]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Flow Properties**")
            st.write(f"Flow Grade: **{exc['flow_grade']}**")
            st.write(f"Carr Index: {exc['carr_index']} %")
            st.write(f"Hausner Ratio: {exc['hausner_ratio']}")
            st.write(f"Angle of Repose: {exc['angle_of_repose']}°")
        
        with col2:
            st.markdown("**Compressibility**")
            st.write(f"Grade: **{exc['compressibility']}**")
            st.write(f"Moisture Sensitive: {exc['moisture_sensitive']}")
            st.write(f"Hygroscopic: {exc['hygroscopic']}")
            st.write(f"Cost: {exc['cost_grade']}")
        
        st.divider()
        st.write(f"**Common Use:** {exc['common_use']}")
        st.write(f"**Max % in formulation:** {exc['max_percent']} %")

# ============================================================
# TAB 4 — DEFECT PREDICTOR
# ============================================================

with tab4:
    st.subheader("Defect Risk Predictor")
    section_rule()

    from mainproject_physicc_engine import (heckel, ryshkewitch, 
                                             fell_newton)
    from machinemodule import (force_to_pressure, speed_to_dwell, 
                                dwell_time_factor)
    from defect_predictor import DEFECT_THRESHOLDS
    
    exc_data  = EXCIPIENT_EXTENDED.get(excipient, {})
    pressure2 = force_to_pressure(force_kN, 8.0)
    dwell_ms  = speed_to_dwell(speed)
    dt_factor = dwell_time_factor(dwell_ms)
    
    r = simulate(excipient, pressure2)
    if r:
        hardness2 = r['hardness'] * dt_factor
        porosity2 = r['porosity']
        
        cap_score,  cap_r  = predict_capping(hardness2, speed, dwell_ms)
        lam_score,  lam_r  = predict_lamination(porosity2, speed, excipient)
        sti_score,  sti_r  = predict_sticking(excipient, temperature)
        twin_score, twin_r = predict_twinning(hardness2, speed, machine_type)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Capping Risk",    f"{cap_score}",  risk_level(cap_score))
        col2.metric("Lamination Risk", f"{lam_score}",  risk_level(lam_score))
        col3.metric("Sticking Risk",   f"{sti_score}",  risk_level(sti_score))
        col4.metric("Twinning Risk",   f"{twin_score}", risk_level(twin_score))
        
        # Risk Chart
        fig2, ax2 = plt.subplots(figsize=(8, 3))
        defects = ['Capping', 'Lamination', 'Sticking', 'Twinning']
        scores  = [cap_score, lam_score, sti_score, twin_score]
        colors  = [NASA["fail"] if s > 50 else NASA["accent"]
                   if s > 25 else NASA["pass"] for s in scores]

        ax2.barh(defects, scores, color=colors)
        ax2.axvline(x=50, color=NASA["fail"], linestyle='--',
                    alpha=0.6, label='High Risk Threshold')
        ax2.set_xlabel("Risk Score")
        ax2.set_title("Defect Risk Analysis")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        st.pyplot(fig2)
        plt.close()

# ============================================================
# TAB 5 — ANIMATION
# ============================================================

with tab5:
    st.subheader("Drill-Down Interactive Simulator")
    section_rule()

    from drill_down_animation import render_drill_down
    from animation_module import detect_defects
    from machinemodule import force_to_pressure, speed_to_dwell, dwell_time_factor

    # คำนวณค่า
    pressure2 = force_to_pressure(force_kN, 8.0)
    dwell_ms  = speed_to_dwell(speed)
    dt_factor = dwell_time_factor(dwell_ms)

    r = simulate(excipient, pressure2)
    if r:
        hardness_dd = r['hardness'] * dt_factor
        porosity_dd = r['porosity']
    else:
        hardness_dd = 100.0
        porosity_dd = 0.1

    defects_dd = detect_defects(
        hardness_dd, porosity_dd, speed,
        excipient, temperature,
        machine_type, dwell_ms
    )

    # Rotation สำหรับ rotary
    if 'rotation_angle' not in st.session_state:
        st.session_state.rotation_angle = 0

    col_r1, col_r2 = st.columns([3, 1])
    with col_r2:
        if st.button("Rotate"):
            st.session_state.rotation_angle = \
                (st.session_state.rotation_angle + 22.5) % 360

    render_drill_down(
        excipient   = excipient,
        hardness    = hardness_dd,
        porosity    = porosity_dd,
        force_kN    = force_kN,
        speed       = speed,
        temperature = temperature,
        defects     = defects_dd,
        rotation    = st.session_state.rotation_angle
    )

    if False:  # legacy single-punch animation (disabled)
        fig3, ax3 = plt.subplots(figsize=(4, 6))
        ax3.set_xlim(0, 4)
        ax3.set_ylim(0, 6)
        ax3.set_aspect('equal')
        ax3.axis('off')
        ax3.set_facecolor('#1a1a2e')
        fig3.patch.set_facecolor('#1a1a2e')
        
        # วาด die (กรอบ)
        die = patches.Rectangle(
            (1, 1.5), 2, 2.5,
            linewidth=2, edgecolor='silver',
            facecolor='#2d2d4e'
        )
        ax3.add_patch(die)
        
        # วาด lower punch
        lower_punch = patches.Rectangle(
            (1, 1), 2, 0.5,
            linewidth=2, edgecolor='#90CAF9',
            facecolor='#1565C0'
        )
        ax3.add_patch(lower_punch)
        
        # วาด powder
        powder = patches.Rectangle(
            (1.05, 1.5), 1.9, 2.0,
            facecolor='#F5F5DC', alpha=0.8
        )
        ax3.add_patch(powder)
        
        # วาด upper punch (จะเคลื่อนที่)
        upper_punch = patches.Rectangle(
            (1, 4.5), 2, 0.5,
            linewidth=2, edgecolor='#90CAF9',
            facecolor='#1565C0'
        )
        ax3.add_patch(upper_punch)
        
        # Label
        ax3.text(2, 5.5, 'Single Punch Press',
                 ha='center', color='white', fontsize=10)
        ax3.text(2, 0.5, f'{excipient}',
                 ha='center', color='#90CAF9', fontsize=8)
        
        placeholder = st.empty()
        
        # Animate punch กดลง
        frames = 20
        for i in range(frames + 10):
            
            ax3.patches[-1].remove()  # ลบ upper punch เดิม
            
            if i < frames:
                # punch กดลง
                y_pos = 4.5 - (i / frames) * 2.0
                powder_h = 2.0 - (i / frames) * 1.0
            else:
                # punch ขึ้น
                j = i - frames
                y_pos = 2.5 + (j / 10) * 2.0
                powder_h = 1.0
            
            upper_punch = patches.Rectangle(
                (1, y_pos), 2, 0.5,
                linewidth=2, edgecolor='#90CAF9',
                facecolor='#1565C0'
            )
            ax3.add_patch(upper_punch)
            
            # Update powder height
            if len(ax3.patches) > 3:
                ax3.patches[2].set_height(powder_h)
            
            placeholder.pyplot(fig3)
            time.sleep(0.05)
        
        # แสดง tablet สุดท้าย
        ax3.text(2, 3.0, '✅ Tablet', 
                 ha='center', color='green', 
                 fontsize=12, fontweight='bold')
        placeholder.pyplot(fig3)
        plt.close()

# ============================================================
with tab6:
    st.subheader("2D Machine Diagram")
    section_rule()

    from rotary_2d import run_rotary_2d_animation
    from single_punch_2d import run_single_punch_2d
    from animation_module import detect_defects
    from machinemodule import (force_to_pressure,
                                speed_to_dwell,
                                dwell_time_factor)

    pressure2 = force_to_pressure(force_kN, 8.0)
    dwell_ms  = speed_to_dwell(speed)
    dt_factor = dwell_time_factor(dwell_ms)
    r         = simulate(excipient, pressure2)

    if r:
        hardness_2d = r['hardness'] * dt_factor
        porosity_2d = r['porosity']
    else:
        hardness_2d = 100.0
        porosity_2d = 0.1

    defects_2d = detect_defects(
        hardness_2d, porosity_2d,
        speed, excipient,
        temperature, machine_type, dwell_ms
    )

    tablet_count = int(speed * 2)
    reject_count = 0 if defects_2d.get("ok", True) \
                   else int(tablet_count * 0.1)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Hardness", f"{hardness_2d:.1f} N")
    col2.metric("Tablets/batch", tablet_count)
    col3.metric("Status",
                "NORMAL" if defects_2d.get("ok", True)
                else "DEFECT")

    # เลือก machine
    machine_2d = st.radio(
        "เลือกเครื่อง",
        ["Single Punch Press", "Rotary Press"],
        horizontal=True
    )

    n_cycles = st.slider("จำนวน cycle", 1, 3, 1)

    if st.button("Run 2D Animation"):
        placeholder = st.empty()

        if machine_2d == "Single Punch Press":
            run_single_punch_2d(
                hardness    = hardness_2d,
                defects     = defects_2d,
                force_kN    = force_kN,
                speed       = speed,
                placeholder = placeholder,
                n_cycles    = n_cycles
            )
        else:
            run_rotary_2d_animation(
                hardness     = hardness_2d,
                defects      = defects_2d,
                tablet_count = tablet_count * 8,
                reject_count = reject_count * 8,
                placeholder  = placeholder,
                n_frames     = 40 * n_cycles
            )

        st.success("Animation complete")