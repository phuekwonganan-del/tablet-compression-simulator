"""
Pharmaceutical Tablet Compression Simulator
Drill-Down Interactive Animation v1.0
Author: Tok
Level 1: Factory View
Level 2: Machine View  
Level 3: Process View (with defects)
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st

# ============================================================
# COLORS
# ============================================================

C = {
    "bg":       "#1a1a2e",
    "punch":    "#1565C0",
    "die":      "#2d2d4e",
    "powder":   "#F5F5DC",
    "tablet":   "#4CAF50",
    "capping":  "#FF5722",
    "lam":      "#FF9800",
    "sticking": "#F44336",
    "twinning": "#9C27B0",
    "text":     "#FFFFFF",
    "accent":   "#90CAF9",
    "wall":     "#37474F",
    "floor":    "#263238",
    "machine1": "#1565C0",
    "machine2": "#6A1B9A",
    "conveyor": "#455A64",
}

# ============================================================
# LEVEL 1 — FACTORY VIEW
# ============================================================

def create_factory_view(hardness, defects):
    """
    Level 1: มองจากนอก factory
    เห็นทั้ง Single Punch และ Rotary Press
    คลิกเครื่องไหน → zoom เข้าไป
    """
    
    fig = go.Figure()
    
    fig.update_layout(
        title=dict(
            text="🏭 Pharmaceutical Manufacturing Facility",
            font=dict(color=C["text"], size=16),
            x=0.5
        ),
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["floor"],
        xaxis=dict(range=[0, 20], showgrid=False,
                   zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 12], showgrid=False,
                   zeroline=False, showticklabels=False),
        height=500,
        showlegend=False,
        annotations=[],
    )
    
    # ===== FLOOR =====
    fig.add_shape(type="rect",
        x0=0, y0=0, x1=20, y1=1,
        fillcolor=C["floor"],
        line=dict(color=C["wall"])
    )
    
    # ===== WALLS =====
    fig.add_shape(type="rect",
        x0=0, y0=0, x1=20, y1=12,
        fillcolor="rgba(0,0,0,0)",
        line=dict(color=C["wall"], width=3)
    )
    
    # ===== SINGLE PUNCH MACHINE =====
    # Body
    fig.add_shape(type="rect",
        x0=2, y0=1, x1=7, y1=8,
        fillcolor=C["machine1"],
        line=dict(color=C["accent"], width=2)
    )
    # Screen
    fig.add_shape(type="rect",
        x0=2.5, y0=5, x1=6.5, y1=7.5,
        fillcolor="#0d47a1",
        line=dict(color=C["accent"], width=1)
    )
    # Hopper
    fig.add_shape(type="path",
        path="M 3.5 8 L 5.5 8 L 5 10 L 4 10 Z",
        fillcolor="#455A64",
        line=dict(color=C["accent"])
    )
    
    # Defect indicator บน single punch
    sp_color = C["capping"] if defects.get("capping") else \
               C["lam"] if defects.get("lamination") else \
               C["tablet"]
    fig.add_shape(type="circle",
        x0=5.5, y0=7.5, x1=6.5, y1=8.5,
        fillcolor=sp_color,
        line=dict(color="white")
    )
    
    # Label Single Punch
    fig.add_annotation(
        x=4.5, y=4.5,
        text="⚙️ Single Punch<br>Press",
        font=dict(color=C["text"], size=11),
        showarrow=False,
        bgcolor="rgba(0,0,0,0.5)"
    )
    
    # Clickable overlay Single Punch
    fig.add_trace(go.Scatter(
        x=[4.5], y=[6],
        mode='markers',
        marker=dict(
            size=80,
            color='rgba(0,0,0,0)',
            line=dict(width=0)
        ),
        name="single_punch",
        hovertext="🖱️ คลิกเพื่อดู Single Punch Press",
        hoverinfo="text",
        customdata=["single_punch"]
    ))
    
    # ===== ROTARY MACHINE =====
    # Body
    fig.add_shape(type="rect",
        x0=10, y0=1, x1=18, y1=9,
        fillcolor=C["machine2"],
        line=dict(color="#CE93D8", width=2)
    )
    
    # Turret (top view circle)
    theta = np.linspace(0, 2*np.pi, 100)
    turret_x = 14 + 2.5 * np.cos(theta)
    turret_y = 5 + 2.5 * np.sin(theta)
    
    fig.add_trace(go.Scatter(
        x=turret_x, y=turret_y,
        fill='toself',
        fillcolor='#4A148C',
        line=dict(color='#CE93D8', width=2),
        hoverinfo='skip',
        showlegend=False
    ))
    
    # Punch stations
    n_stations = 16
    for i in range(n_stations):
        angle = (2 * np.pi / n_stations) * i
        px = 14 + 2.0 * np.cos(angle)
        py = 5 + 2.0 * np.sin(angle)
        
        punch_color = C["capping"] if defects.get("capping") else \
                      C["tablet"]
        
        fig.add_shape(type="circle",
            x0=px-0.2, y0=py-0.2,
            x1=px+0.2, y1=py+0.2,
            fillcolor=punch_color,
            line=dict(color="white", width=1)
        )
    
    # Defect indicator บน rotary
    rot_color = C["twinning"] if defects.get("twinning") else \
                C["sticking"] if defects.get("sticking") else \
                C["tablet"]
    fig.add_shape(type="circle",
        x0=16.5, y0=8, x1=17.5, y1=9,
        fillcolor=rot_color,
        line=dict(color="white")
    )
    
    # Label Rotary
    fig.add_annotation(
        x=14, y=2,
        text="🔄 Rotary Press<br>(16 Stations)",
        font=dict(color=C["text"], size=11),
        showarrow=False,
        bgcolor="rgba(0,0,0,0.5)"
    )
    
    # Clickable overlay Rotary
    fig.add_trace(go.Scatter(
        x=[14], y=[5],
        mode='markers',
        marker=dict(
            size=120,
            color='rgba(0,0,0,0)',
            line=dict(width=0)
        ),
        name="rotary",
        hovertext="🖱️ คลิกเพื่อดู Rotary Press",
        hoverinfo="text",
        customdata=["rotary"]
    ))
    
    # ===== CONVEYOR BELT =====
    fig.add_shape(type="rect",
        x0=7, y0=1, x1=10, y1=1.8,
        fillcolor=C["conveyor"],
        line=dict(color=C["accent"])
    )
    fig.add_annotation(
        x=8.5, y=2.2,
        text="→ Conveyor",
        font=dict(color=C["accent"], size=9),
        showarrow=False
    )
    
    # ===== HARDNESS INDICATOR =====
    hardness_color = "#4CAF50" if 40 <= hardness <= 200 else "#FF5722"
    fig.add_annotation(
        x=10, y=11,
        text=f"📊 Hardness: {hardness:.1f} N | " +
             ("✅ QC Pass" if 40 <= hardness <= 200 else "❌ QC Fail"),
        font=dict(color=hardness_color, size=12),
        showarrow=False,
        bgcolor="rgba(0,0,0,0.7)"
    )
    
    # ===== LEGEND =====
    fig.add_annotation(
        x=1, y=11.5,
        text="🟢 Normal  🔴 Capping  🟠 Lamination  🟣 Twinning  🔴 Sticking",
        font=dict(color=C["text"], size=9),
        showarrow=False,
        xanchor="left"
    )
    
    return fig

# ============================================================
# LEVEL 2 — SINGLE PUNCH VIEW
# ============================================================

def create_single_punch_view(hardness, porosity, 
                              force_kN, speed, defects):
    """
    Level 2: Single Punch Press แบบ detailed
    เห็น Hopper, Die, Punch, Tablet output
    """
    
    fig = go.Figure()
    
    fig.update_layout(
        title=dict(
            text="⚙️ Single Punch Press — Detailed View",
            font=dict(color=C["text"], size=14),
            x=0.5
        ),
        paper_bgcolor=C["bg"],
        plot_bgcolor="#16213e",
        xaxis=dict(range=[0, 10], showgrid=False,
                   zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 14], showgrid=False,
                   zeroline=False, showticklabels=False),
        height=600,
        showlegend=False,
    )
    
    tablet_color = C["capping"] if defects.get("capping") else \
                   C["lam"] if defects.get("lamination") else \
                   C["sticking"] if defects.get("sticking") else \
                   C["tablet"]
    
    # ===== HOPPER =====
    fig.add_shape(type="path",
        path="M 3 14 L 7 14 L 6 11 L 4 11 Z",
        fillcolor="#455A64",
        line=dict(color=C["accent"], width=2)
    )
    fig.add_annotation(x=5, y=13,
        text="📦 Powder Hopper",
        font=dict(color=C["text"], size=9),
        showarrow=False
    )
    
    # Powder falling
    for i in range(5):
        fig.add_shape(type="circle",
            x0=4.5+i*0.2, y0=10.5-i*0.3,
            x1=4.7+i*0.2, y1=10.7-i*0.3,
            fillcolor=C["powder"],
            line=dict(color=C["powder"])
        )
    
    # ===== UPPER PUNCH =====
    fig.add_shape(type="rect",
        x0=3.5, y0=9, x1=6.5, y1=10.5,
        fillcolor=C["punch"],
        line=dict(color=C["accent"], width=2)
    )
    # Punch rod
    fig.add_shape(type="rect",
        x0=4.7, y0=10.5, x1=5.3, y1=12,
        fillcolor="#0d47a1",
        line=dict(color=C["accent"])
    )
    fig.add_annotation(x=7.5, y=9.8,
        text=f"↓ {force_kN:.0f} kN",
        font=dict(color="#FF5722", size=11, family="bold"),
        showarrow=False
    )
    
    # ===== DIE =====
    # Left wall
    fig.add_shape(type="rect",
        x0=3, y0=5, x1=3.7, y1=9,
        fillcolor=C["die"],
        line=dict(color="#7986CB", width=2)
    )
    # Right wall
    fig.add_shape(type="rect",
        x0=6.3, y0=5, x1=7, y1=9,
        fillcolor=C["die"],
        line=dict(color="#7986CB", width=2)
    )
    
    # Powder in die
    fig.add_shape(type="rect",
        x0=3.7, y0=5, x1=6.3, y1=8.5,
        fillcolor=C["powder"],
        opacity=0.8,
        line=dict(color=C["powder"])
    )
    
    # ===== LOWER PUNCH =====
    fig.add_shape(type="rect",
        x0=3.5, y0=3.5, x1=6.5, y1=5,
        fillcolor=C["punch"],
        line=dict(color=C["accent"], width=2)
    )
    fig.add_shape(type="rect",
        x0=4.7, y0=2, x1=5.3, y1=3.5,
        fillcolor="#0d47a1",
        line=dict(color=C["accent"])
    )
    
    # ===== TABLET OUTPUT =====
    if defects.get("capping"):
        # Capping — หัวแยก
        fig.add_shape(type="rect",
            x0=7.5, y0=5, x1=9.5, y1=5.8,
            fillcolor=tablet_color, opacity=0.9,
            line=dict(color="white")
        )
        fig.add_shape(type="rect",
            x0=7.5, y0=6.2, x1=9.5, y1=6.6,
            fillcolor=tablet_color, opacity=0.6,
            line=dict(color="white", dash="dash")
        )
        fig.add_annotation(x=8.5, y=7,
            text="⚠️ CAPPING",
            font=dict(color=C["capping"], size=10),
            showarrow=False
        )
    
    elif defects.get("lamination"):
        # Lamination
        for layer in range(3):
            fig.add_shape(type="rect",
                x0=7.5, y0=5+layer*0.35, x1=9.5, y1=5.25+layer*0.35,
                fillcolor=tablet_color,
                opacity=0.9-layer*0.1,
                line=dict(color="white", dash="dash")
            )
        fig.add_annotation(x=8.5, y=6.5,
            text="⚠️ LAMINATION",
            font=dict(color=C["lam"], size=10),
            showarrow=False
        )
    
    elif defects.get("twinning"):
        # Twinning — 2 เม็ดติดกัน
        fig.add_shape(type="circle",
            x0=7.3, y0=5, x1=8.5, y1=5.8,
            fillcolor=tablet_color, opacity=0.9,
            line=dict(color="white")
        )
        fig.add_shape(type="circle",
            x0=8.3, y0=5, x1=9.5, y1=5.8,
            fillcolor=tablet_color, opacity=0.9,
            line=dict(color="white")
        )
        fig.add_annotation(x=8.5, y=6.3,
            text="⚠️ TWINNING",
            font=dict(color=C["twinning"], size=10),
            showarrow=False
        )
    
    else:
        # Normal tablet
        fig.add_shape(type="rect",
            x0=7.5, y0=5, x1=9.5, y1=5.8,
            fillcolor=tablet_color, opacity=0.95,
            line=dict(color="white", width=2)
        )
        fig.add_annotation(x=8.5, y=6.3,
            text="✅ Normal",
            font=dict(color=C["tablet"], size=10),
            showarrow=False
        )
    
    # ===== LABELS =====
    fig.add_annotation(x=5, y=0.8,
        text=f"Speed: {speed} rpm | Force: {force_kN:.0f} kN | Hardness: {hardness:.1f} N",
        font=dict(color=C["accent"], size=10),
        showarrow=False,
        bgcolor="rgba(0,0,0,0.5)"
    )
    
    # ===== FORCE METER =====
    force_pct = min(force_kN / 100, 1.0)
    fig.add_shape(type="rect",
        x0=0.5, y0=2, x1=1.2, y1=2+force_pct*8,
        fillcolor="#FF5722" if force_pct > 0.8 else
                  "#FF9800" if force_pct > 0.5 else "#4CAF50",
        line=dict(color="white")
    )
    fig.add_annotation(x=0.85, y=1.5,
        text="Force",
        font=dict(color=C["text"], size=8),
        showarrow=False
    )
    
    # ===== POROSITY METER =====
    por_pct = min(porosity / 0.5, 1.0)
    fig.add_shape(type="rect",
        x0=1.5, y0=2, x1=2.2, y1=2+por_pct*8,
        fillcolor="#2196F3",
        line=dict(color="white")
    )
    fig.add_annotation(x=1.85, y=1.5,
        text="Porosity",
        font=dict(color=C["text"], size=8),
        showarrow=False
    )
    
    return fig

# ============================================================
# LEVEL 2 — ROTARY VIEW
# ============================================================

def create_rotary_view(hardness, speed, defects, rotation=0):
    """
    Level 2: Rotary Press แบบ detailed
    Top view เห็น turret + stations ชัดเจน
    """
    
    fig = go.Figure()
    
    fig.update_layout(
        title=dict(
            text="🔄 Rotary Press — 16 Stations Top View",
            font=dict(color=C["text"], size=14),
            x=0.5
        ),
        paper_bgcolor=C["bg"],
        plot_bgcolor="#16213e",
        xaxis=dict(range=[-7, 7], showgrid=False,
                   zeroline=False, showticklabels=False,
                   scaleanchor="y"),
        yaxis=dict(range=[-7, 7], showgrid=False,
                   zeroline=False, showticklabels=False),
        height=600,
        showlegend=True,
    )
    
    tablet_color = C["capping"] if defects.get("capping") else \
                   C["twinning"] if defects.get("twinning") else \
                   C["sticking"] if defects.get("sticking") else \
                   C["tablet"]
    
    # ===== TURRET =====
    theta = np.linspace(0, 2*np.pi, 100)
    
    # Outer ring
    fig.add_trace(go.Scatter(
        x=5*np.cos(theta), y=5*np.sin(theta),
        fill='toself', fillcolor='#37474F',
        line=dict(color='#78909C', width=3),
        hoverinfo='skip', showlegend=False
    ))
    
    # Inner ring
    fig.add_trace(go.Scatter(
        x=3.5*np.cos(theta), y=3.5*np.sin(theta),
        fill='toself', fillcolor='#4A148C',
        line=dict(color='#CE93D8', width=2),
        hoverinfo='skip', showlegend=False
    ))
    
    # Center hub
    fig.add_trace(go.Scatter(
        x=1.2*np.cos(theta), y=1.2*np.sin(theta),
        fill='toself', fillcolor=C["punch"],
        line=dict(color=C["accent"], width=2),
        hoverinfo='skip', showlegend=False
    ))
    
    # Rotation indicator
    rot_rad = np.radians(rotation)
    fig.add_trace(go.Scatter(
        x=[0, np.cos(rot_rad)*1.0],
        y=[0, np.sin(rot_rad)*1.0],
        mode='lines',
        line=dict(color=C["accent"], width=3),
        hoverinfo='skip', showlegend=False
    ))
    
    # ===== 16 PUNCH STATIONS =====
    n_stations = 16
    
    zone_colors = {
        "compression": "#FF5722",
        "ejection":    tablet_color,
        "filling":     C["powder"],
        "transit":     C["punch"],
    }
    
    for i in range(n_stations):
        angle_deg = (360/n_stations)*i + rotation
        angle_rad = np.radians(angle_deg)
        norm_angle = angle_deg % 360
        
        px = 4.2 * np.cos(angle_rad)
        py = 4.2 * np.sin(angle_rad)
        
        # Zone detection
        if 75 <= norm_angle <= 105:
            zone = "compression"
            size = 12
        elif 345 <= norm_angle or norm_angle <= 15:
            zone = "ejection"
            size = 14
        elif 255 <= norm_angle <= 285:
            zone = "filling"
            size = 11
        else:
            zone = "transit"
            size = 10
        
        punch_color = zone_colors[zone]
        
        fig.add_trace(go.Scatter(
            x=[px], y=[py],
            mode='markers+text',
            marker=dict(
                size=size,
                color=punch_color,
                line=dict(color='white', width=1.5),
                symbol='circle'
            ),
            text=str(i+1),
            textfont=dict(size=6, color='white'),
            textposition='middle center',
            hovertext=f"Station {i+1}<br>Zone: {zone}<br>Hardness: {hardness:.1f} N",
            hoverinfo='text',
            showlegend=False
        ))
        
        # Tablet ออกมาตรง ejection
        if 345 <= norm_angle or norm_angle <= 15:
            ex = 5.8 * np.cos(angle_rad)
            ey = 5.8 * np.sin(angle_rad)
            
            if defects.get("twinning"):
                fig.add_trace(go.Scatter(
                    x=[ex-0.2, ex+0.2], y=[ey, ey],
                    mode='markers',
                    marker=dict(size=8, color=tablet_color,
                               line=dict(color='white', width=1)),
                    hoverinfo='skip', showlegend=False
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=[ex], y=[ey],
                    mode='markers',
                    marker=dict(size=10, color=tablet_color,
                               symbol='circle',
                               line=dict(color='white', width=1.5)),
                    hoverinfo='skip', showlegend=False
                ))
    
    # ===== ZONE LABELS =====
    fig.add_annotation(x=0, y=6, text="⚡ COMPRESSION",
        font=dict(color="#FF5722", size=10, family="bold"),
        showarrow=False)
    
    fig.add_annotation(x=6, y=0, text="📤 EJECTION",
        font=dict(color=tablet_color, size=10, family="bold"),
        showarrow=False, textangle=-90)
    
    fig.add_annotation(x=0, y=-6, text="📥 FILLING",
        font=dict(color=C["powder"], size=10, family="bold"),
        showarrow=False)
    
    # ===== INFO BOX =====
    defect_text = "✅ Normal"
    if defects.get("capping"):
        defect_text = "⚠️ CAPPING"
    elif defects.get("twinning"):
        defect_text = "⚠️ TWINNING"
    elif defects.get("sticking"):
        defect_text = "⚠️ STICKING"
    
    fig.add_annotation(x=-6, y=6,
        text=f"Speed: {speed} rpm<br>" +
             f"Hardness: {hardness:.1f} N<br>" +
             f"Status: {defect_text}",
        font=dict(color=C["text"], size=10),
        showarrow=False,
        bgcolor="rgba(0,0,0,0.7)",
        bordercolor=C["accent"],
        borderwidth=1,
        align="left"
    )
    
    return fig

# ============================================================
# STREAMLIT DRILL-DOWN UI
# ============================================================

def render_drill_down(excipient, hardness, porosity,
                       force_kN, speed, temperature,
                       defects, rotation=0):
    """
    Main function สำหรับ Streamlit
    จัดการ Level 1, 2, 3
    """
    
    # Session state สำหรับ track level
    if 'drill_level' not in st.session_state:
        st.session_state.drill_level = 1
    if 'selected_machine' not in st.session_state:
        st.session_state.selected_machine = None
    
    # ===== BREADCRUMB =====
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("🏭 Factory"):
            st.session_state.drill_level = 1
            st.session_state.selected_machine = None
    
    with col2:
        if st.session_state.drill_level >= 2:
            machine_label = "⚙️ Single" \
                if st.session_state.selected_machine == "single" \
                else "🔄 Rotary"
            if st.button(machine_label):
                st.session_state.drill_level = 2
    
    with col3:
        level_text = {
            1: "📍 Level 1: Factory Overview",
            2: "📍 Level 2: Machine Detail",
        }
        st.caption(level_text.get(st.session_state.drill_level, ""))
    
    st.divider()
    
    # ===== LEVEL 1: FACTORY VIEW =====
    if st.session_state.drill_level == 1:
        
        fig = create_factory_view(hardness, defects)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 คลิกปุ่มด้านล่างเพื่อ zoom เข้าไปในเครื่อง")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚙️ เข้าไปดู Single Punch Press",
                         use_container_width=True):
                st.session_state.drill_level = 2
                st.session_state.selected_machine = "single"
                st.rerun()
        
        with col2:
            if st.button("🔄 เข้าไปดู Rotary Press",
                         use_container_width=True):
                st.session_state.drill_level = 2
                st.session_state.selected_machine = "rotary"
                st.rerun()
    
    # ===== LEVEL 2: MACHINE VIEW =====
    elif st.session_state.drill_level == 2:
        
        if st.session_state.selected_machine == "single":
            fig = create_single_punch_view(
                hardness, porosity, force_kN, speed, defects
            )
        else:
            fig = create_rotary_view(
                hardness, speed, defects, rotation
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Defect summary
        if not defects.get("ok", True):
            st.error("⚠️ พบ Defect — ปรับ Parameters เพื่อแก้ไข")
            
            cols = st.columns(4)
            defect_list = [
                ("Capping",    defects.get("capping"),    "ลด Force หรือ Speed"),
                ("Lamination", defects.get("lamination"), "ลด Speed"),
                ("Sticking",   defects.get("sticking"),   "ลด Temperature"),
                ("Twinning",   defects.get("twinning"),   "ลด Speed"),
            ]
            
            for i, (name, active, fix) in enumerate(defect_list):
                with cols[i]:
                    if active:
                        st.error(f"🔴 {name}\n{fix}")
                    else:
                        st.success(f"✅ {name}")
        else:
            st.success("✅ ไม่พบ Defect — Process ปลอดภัย")