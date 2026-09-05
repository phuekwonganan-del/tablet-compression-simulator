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
    page_icon="💊",
    layout="wide"
)

st.title("💊 Pharmaceutical Tablet Compression Simulator")
st.caption("by Tok | Physics Engine v1.0 | QbD Framework")

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Parameters")

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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧪 Physics Engine",
    "⚙️ Machine Simulation",
    "📦 Excipient Profile",
    "⚠️ Defect Predictor",
    "🎬 Animation"
])

# ============================================================
# TAB 1 — PHYSICS ENGINE
# ============================================================

with tab1:
    st.subheader("Physics Engine — Heckel + Ryshkewitch + Fell-Newton")
    
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
                color='#2196F3', linewidth=2, label='Hardness')
        ax.axhline(y=40,  color='green', linestyle='--', 
                   alpha=0.7, label='USP min (40 N)')
        ax.axhline(y=200, color='red',   linestyle='--', 
                   alpha=0.7, label='USP max (200 N)')
        ax.axvline(x=pressure, color='orange', linestyle='-', 
                   alpha=0.7, label=f'Current ({pressure} MPa)')
        ax.fill_between(pressures, 40, 200, alpha=0.1, color='green')
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
        colors  = ['red' if s > 50 else 'orange' 
                   if s > 25 else 'green' for s in scores]
        
        ax2.barh(defects, scores, color=colors)
        ax2.axvline(x=50, color='red', linestyle='--', 
                    alpha=0.5, label='High Risk Threshold')
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
    st.subheader("🎬 Real-time Animation — Side by Side")

    from animation_module import run_side_by_side_animation
    from mainproject_physicc_engine import heckel, ryshkewitch, fell_newton
    from machinemodule import force_to_pressure, speed_to_dwell, dwell_time_factor
    import math

    # คำนวณค่าจาก sidebar
    exc_data  = EXCIPIENT_EXTENDED.get(excipient, {})
    pressure2 = force_to_pressure(force_kN, 8.0)
    dwell_ms  = speed_to_dwell(speed)
    dt_factor = dwell_time_factor(dwell_ms)

    r = simulate(excipient, pressure2)
    if r:
        hardness_anim = r['hardness'] * dt_factor
        porosity_anim = r['porosity']
    else:
        hardness_anim = 100.0
        porosity_anim = 0.1

    # Info
    col1, col2, col3 = st.columns(3)
    col1.metric("Hardness", f"{hardness_anim:.1f} N")
    col2.metric("Dwell Time", f"{dwell_ms:.1f} ms")
    col3.metric("Pressure", f"{pressure2:.1f} MPa")

    st.info("💡 ปรับ slider ซ้ายมือ แล้วกด Run เพื่อดู animation")

    n_cycles = st.slider("จำนวน cycle", 1, 5, 2)

    if st.button("▶️ Run Animation"):
        placeholder = st.empty()
        run_side_by_side_animation(
            excipient    = excipient,
            hardness     = hardness_anim,
            porosity     = porosity_anim,
            force_kN     = force_kN,
            speed        = speed,
            temperature  = temperature,
            machine_type = machine_type,
            dwell_ms     = dwell_ms,
            placeholder  = placeholder,
            n_cycles     = n_cycles
        )
        st.success("✅ Animation เสร็จแล้ว")

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