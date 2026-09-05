"""
Pharmaceutical Tablet Compression Simulator
Animation Module v1.0
Author: Tok
Real-time interactive animation with defect visualization
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np
import time

# ============================================================
# COLOR SCHEME
# ============================================================

COLORS = {
    "background":  "#1a1a2e",
    "punch":       "#1565C0",
    "punch_edge":  "#90CAF9",
    "die":         "#2d2d4e",
    "die_edge":    "#7986CB",
    "powder":      "#F5F5DC",
    "tablet_ok":   "#4CAF50",
    "tablet_cap":  "#FF5722",
    "tablet_lam":  "#FF9800",
    "tablet_twin": "#9C27B0",
    "tablet_stick":"#F44336",
    "text":        "#FFFFFF",
    "accent":      "#90CAF9",
    "warning":     "#FF5722",
    "ok":          "#4CAF50",
    "turret":      "#37474F",
    "turret_edge": "#78909C",
}

# ============================================================
# DEFECT DETECTION
# ============================================================

def detect_defects(hardness, porosity, speed, 
                   excipient_name, temperature,
                   machine_type, dwell_ms):
    """
    ตรวจสอบ defect จากค่าที่คำนวณได้
    คืนค่า dict ของ defect ที่เกิดขึ้น
    """
    defects = {
        "capping":    False,
        "lamination": False,
        "sticking":   False,
        "twinning":   False,
        "ok":         True,
    }
    
    # Capping
    if hardness > 350 or (speed > 50 and dwell_ms < 10):
        defects["capping"] = True
        defects["ok"] = False
    
    # Lamination
    if porosity > 0.25 and speed > 45:
        defects["lamination"] = True
        defects["ok"] = False
    
    # Sticking (ใช้ค่าพื้นฐาน)
    if temperature > 35:
        defects["sticking"] = True
        defects["ok"] = False
    
    # Twinning
    if machine_type == "single" and speed > 50 and hardness < 60:
        defects["twinning"] = True
        defects["ok"] = False
    
    return defects


def get_tablet_color(defects):
    """เลือกสีเม็ดยาตาม defect"""
    if defects["capping"]:
        return COLORS["tablet_cap"],   "CAPPING"
    elif defects["lamination"]:
        return COLORS["tablet_lam"],   "LAMINATION"
    elif defects["sticking"]:
        return COLORS["tablet_stick"], "STICKING"
    elif defects["twinning"]:
        return COLORS["tablet_twin"],  "TWINNING"
    else:
        return COLORS["tablet_ok"],    "OK ✅"

# ============================================================
# SINGLE PUNCH ANIMATION
# ============================================================

def draw_single_punch_frame(ax, phase, progress, 
                             defects, hardness, 
                             force_kN, excipient):
    """
    วาด Single Punch Press ใน 1 frame
    
    phase:
    0 = Filling (powder เข้า die)
    1 = Compression (punch กดลง)
    2 = Ejection (tablet ออก)
    
    progress: 0.0 → 1.0 (ความคืบหน้าใน phase นั้น)
    """
    
    ax.clear()
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 10)
    ax.set_facecolor(COLORS["background"])
    ax.axis('off')
    
    tablet_color, defect_label = get_tablet_color(defects)
    
    # ===== MACHINE FRAME =====
    # กรอบเครื่อง
    frame = patches.FancyBboxPatch(
        (0.3, 0.5), 5.4, 9,
        boxstyle="round,pad=0.1",
        linewidth=2,
        edgecolor=COLORS["die_edge"],
        facecolor="#16213e",
        alpha=0.5
    )
    ax.add_patch(frame)
    
    # ===== DIE =====
    die_x, die_y = 1.5, 3.5
    die_w, die_h = 3.0, 2.5
    
    die = patches.Rectangle(
        (die_x, die_y), die_w, die_h,
        linewidth=2,
        edgecolor=COLORS["die_edge"],
        facecolor=COLORS["die"]
    )
    ax.add_patch(die)
    
    # ===== LOWER PUNCH =====
    lower_y = die_y - 0.6
    lower_punch = patches.FancyBboxPatch(
        (die_x + 0.1, lower_y), die_w - 0.2, 0.6,
        boxstyle="round,pad=0.05",
        linewidth=2,
        edgecolor=COLORS["punch_edge"],
        facecolor=COLORS["punch"]
    )
    ax.add_patch(lower_punch)
    
    # ===== POWDER / TABLET =====
    if phase == 0:
        # Filling phase — powder เข้า die
        powder_h = 2.0 * progress
        powder = patches.Rectangle(
            (die_x + 0.1, die_y), die_w - 0.2, powder_h,
            facecolor=COLORS["powder"],
            alpha=0.8
        )
        ax.add_patch(powder)
        
        # powder particles ลงมา
        for i in range(int(10 * progress)):
            px = die_x + 0.2 + np.random.random() * (die_w - 0.4)
            py = die_y + die_h - np.random.random() * 0.5
            ax.plot(px, py, 'o',
                   color=COLORS["powder"],
                   markersize=2, alpha=0.6)
    
    elif phase == 1:
        # Compression phase — punch กดลง
        powder_h = 2.0 - progress * 1.2
        powder_h = max(powder_h, 0.3)
        
        powder = patches.Rectangle(
            (die_x + 0.1, die_y), die_w - 0.2, powder_h,
            facecolor=COLORS["powder"],
            alpha=0.9
        )
        ax.add_patch(powder)
        
        # Upper punch กดลงมา
        upper_y = die_y + die_h + 1.5 - progress * (die_h + 1.0)
        
        upper_punch = patches.FancyBboxPatch(
            (die_x + 0.1, upper_y), die_w - 0.2, 0.6,
            boxstyle="round,pad=0.05",
            linewidth=2,
            edgecolor=COLORS["punch_edge"],
            facecolor=COLORS["punch"]
        )
        ax.add_patch(upper_punch)
        
        # Force indicator (ข้างๆ)
        force_bar_h = progress * 3.0
        force_bar = patches.Rectangle(
            (5.2, 3.5), 0.4, force_bar_h,
            facecolor='#FF5722' if force_bar_h > 2.5 else '#FF9800'
            if force_bar_h > 1.5 else '#4CAF50'
        )
        ax.add_patch(force_bar)
        ax.text(5.4, 3.2, 'Force', ha='center',
                color=COLORS["text"], fontsize=6)
        ax.text(5.4, 3.4 + force_bar_h, f'{force_kN:.0f}kN',
                ha='center', color=COLORS["text"], fontsize=6)
    
    elif phase == 2:
        # Ejection phase — tablet ออกมา
        
        if defects["sticking"]:
            # Sticking — tablet ติด upper punch
            tablet_y = die_y + 0.5 + progress * 0.5
        else:
            tablet_y = die_y + progress * 2.5
        
        # วาด tablet
        if defects["capping"]:
            # Capping — หัวแยก
            body = patches.FancyBboxPatch(
                (die_x + 0.3, tablet_y),
                die_w - 0.6, 0.5,
                boxstyle="round,pad=0.05",
                facecolor=tablet_color, alpha=0.9
            )
            cap = patches.FancyBboxPatch(
                (die_x + 0.3, tablet_y + 0.5 + progress * 0.3),
                die_w - 0.6, 0.2,
                boxstyle="round,pad=0.05",
                facecolor=tablet_color, alpha=0.7
            )
            ax.add_patch(body)
            ax.add_patch(cap)
        
        elif defects["twinning"] and progress > 0.5:
            # Twinning — 2 เม็ดติดกัน
            twin1 = patches.Ellipse(
                (die_x + 1.0, tablet_y + 0.3),
                1.0, 0.5,
                facecolor=tablet_color, alpha=0.9
            )
            twin2 = patches.Ellipse(
                (die_x + 2.0, tablet_y + 0.3),
                1.0, 0.5,
                facecolor=tablet_color, alpha=0.9
            )
            ax.add_patch(twin1)
            ax.add_patch(twin2)
        
        elif defects["lamination"]:
            # Lamination — แตกเป็นชั้น
            for layer in range(3):
                lam = patches.FancyBboxPatch(
                    (die_x + 0.3,
                     tablet_y + layer * 0.25 + progress * layer * 0.1),
                    die_w - 0.6, 0.2,
                    boxstyle="round,pad=0.02",
                    facecolor=tablet_color,
                    alpha=0.8 - layer * 0.1
                )
                ax.add_patch(lam)
        
        else:
            # Normal tablet
            tablet = patches.FancyBboxPatch(
                (die_x + 0.3, tablet_y),
                die_w - 0.6, 0.6,
                boxstyle="round,pad=0.08",
                linewidth=1,
                edgecolor='white',
                facecolor=tablet_color,
                alpha=0.95
            )
            ax.add_patch(tablet)
        
        # Upper punch ค้างอยู่ด้านบน
        upper_punch = patches.FancyBboxPatch(
            (die_x + 0.1, die_y + die_h + 1.5),
            die_w - 0.2, 0.6,
            boxstyle="round,pad=0.05",
            linewidth=2,
            edgecolor=COLORS["punch_edge"],
            facecolor=COLORS["punch"]
        )
        ax.add_patch(upper_punch)
    
    # ===== UPPER PUNCH (ตอนไม่ได้ compress) =====
    if phase == 0:
        upper_punch = patches.FancyBboxPatch(
            (die_x + 0.1, die_y + die_h + 1.5),
            die_w - 0.2, 0.6,
            boxstyle="round,pad=0.05",
            linewidth=2,
            edgecolor=COLORS["punch_edge"],
            facecolor=COLORS["punch"]
        )
        ax.add_patch(upper_punch)
    
    # ===== LABELS =====
    phase_labels = ["📥 Filling", "⚡ Compression", "📤 Ejection"]
    ax.text(3, 9.5, "Single Punch Press",
            ha='center', va='top',
            color=COLORS["text"],
            fontsize=9, fontweight='bold')
    
    ax.text(3, 9.0, phase_labels[phase],
            ha='center', va='top',
            color=COLORS["accent"],
            fontsize=8)
    
    ax.text(3, 0.8, f"Excipient: {excipient}",
            ha='center', color=COLORS["accent"], fontsize=7)
    
    ax.text(3, 0.4, f"Hardness: {hardness:.1f} N",
            ha='center', color=COLORS["text"], fontsize=7)
    
    # Defect label
    if not defects["ok"]:
        ax.text(3, 1.3, f"⚠️ {defect_label}",
                ha='center',
                color=COLORS["warning"],
                fontsize=8, fontweight='bold')

# ============================================================
# ROTARY PRESS ANIMATION
# ============================================================

def draw_rotary_frame(ax, rotation_angle, defects, 
                       hardness, speed, excipient):
    """
    วาด Rotary Press แบบ Top View
    เห็น turret หมุน + punch 16 ตัว
    """
    
    ax.clear()
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_facecolor(COLORS["background"])
    ax.set_aspect('equal')
    ax.axis('off')
    
    tablet_color, defect_label = get_tablet_color(defects)
    
    n_stations = 16
    turret_r   = 4.0
    punch_r    = 0.35
    
    # ===== TURRET =====
    turret = plt.Circle(
        (0, 0), turret_r + 0.5,
        color=COLORS["turret"],
        linewidth=2,
        ec=COLORS["turret_edge"]
    )
    ax.add_patch(turret)
    
    # Center hub
    hub = plt.Circle(
        (0, 0), 1.0,
        color=COLORS["punch"],
        ec=COLORS["punch_edge"],
        linewidth=2
    )
    ax.add_patch(hub)
    
    # Rotation indicator
    ax.plot([0, np.cos(np.radians(rotation_angle)) * 0.8],
            [0, np.sin(np.radians(rotation_angle)) * 0.8],
            color=COLORS["accent"], linewidth=2)
    
    # ===== PUNCH STATIONS =====
    for i in range(n_stations):
        
        angle_deg = (360 / n_stations) * i + rotation_angle
        angle_rad = np.radians(angle_deg)
        
        px = turret_r * np.cos(angle_rad)
        py = turret_r * np.sin(angle_rad)
        
        # Zone detection
        # Compression zone = top (80°-100°)
        # Ejection zone    = right (350°-10°)
        # Filling zone     = bottom (260°-280°)
        
        norm_angle = angle_deg % 360
        
        if 75 <= norm_angle <= 105:
            # Compression zone
            punch_color = '#FF5722'
            punch_size  = punch_r * 0.7
        elif 350 <= norm_angle or norm_angle <= 10:
            # Ejection zone
            punch_color = tablet_color
            punch_size  = punch_r * 1.1
        elif 255 <= norm_angle <= 285:
            # Filling zone
            punch_color = COLORS["powder"]
            punch_size  = punch_r
        else:
            # Transit zone
            punch_color = COLORS["punch"]
            punch_size  = punch_r
        
        punch_circle = plt.Circle(
            (px, py), punch_size,
            color=punch_color,
            ec=COLORS["punch_edge"],
            linewidth=1,
            zorder=3
        )
        ax.add_patch(punch_circle)
        
        # Tablet ออกมาตรง ejection zone
        if 350 <= norm_angle or norm_angle <= 10:
            tablet_x = px + np.cos(angle_rad) * 1.2
            tablet_y = py + np.sin(angle_rad) * 1.2
            
            if defects["twinning"]:
                # Twin tablets
                t1 = plt.Circle(
                    (tablet_x - 0.15, tablet_y),
                    0.25, color=tablet_color, alpha=0.8
                )
                t2 = plt.Circle(
                    (tablet_x + 0.15, tablet_y),
                    0.25, color=tablet_color, alpha=0.8
                )
                ax.add_patch(t1)
                ax.add_patch(t2)
            else:
                tablet = plt.Circle(
                    (tablet_x, tablet_y),
                    0.3, color=tablet_color,
                    alpha=0.9, zorder=4
                )
                ax.add_patch(tablet)
    
    # ===== ZONE LABELS =====
    ax.text(0, 5.2, "⚡ Compression",
            ha='center', color='#FF5722',
            fontsize=7, fontweight='bold')
    
    ax.text(5.2, 0, "📤 Eject",
            ha='center', color=tablet_color,
            fontsize=7, rotation=-90)
    
    ax.text(0, -5.2, "📥 Fill",
            ha='center', color=COLORS["powder"],
            fontsize=7, fontweight='bold')
    
    # ===== INFO =====
    ax.text(0, 5.8, "Rotary Press (16 stations)",
            ha='center', color=COLORS["text"],
            fontsize=8, fontweight='bold')
    
    ax.text(-5.5, -5.5, f"Speed: {speed} rpm",
            color=COLORS["accent"], fontsize=7)
    ax.text(-5.5, -5.9, f"Hardness: {hardness:.1f} N",
            color=COLORS["text"], fontsize=7)
    ax.text(-5.5, -6.3, f"Excipient: {excipient}",
            color=COLORS["accent"], fontsize=7)
    
    if not defects["ok"]:
        ax.text(0, -5.8, f"⚠️ {defect_label}",
                ha='center',
                color=COLORS["warning"],
                fontsize=8, fontweight='bold')

# ============================================================
# STREAMLIT INTEGRATION
# ============================================================

def run_side_by_side_animation(excipient, hardness, porosity,
                                force_kN, speed, temperature,
                                machine_type, dwell_ms,
                                placeholder, n_cycles=2):
    """
    รัน animation แบบ side by side
    Single Punch (ซ้าย) + Rotary (ขวา)
    """
    
    defects = detect_defects(
        hardness, porosity, speed,
        excipient, temperature,
        machine_type, dwell_ms
    )
    
    rotation = 0
    
    # Single punch phases
    total_frames = 60 * n_cycles
    
    for frame in range(total_frames):
        
        fig = plt.figure(figsize=(12, 6))
        fig.patch.set_facecolor(COLORS["background"])
        
        gs = gridspec.GridSpec(1, 2, figure=fig)
        ax_single = fig.add_subplot(gs[0, 0])
        ax_rotary  = fig.add_subplot(gs[0, 1])
        
        # Single punch phase
        cycle_frame = frame % 60
        
        if cycle_frame < 20:
            phase    = 0
            progress = cycle_frame / 20
        elif cycle_frame < 40:
            phase    = 1
            progress = (cycle_frame - 20) / 20
        else:
            phase    = 2
            progress = (cycle_frame - 40) / 20
        
        # วาด single punch
        draw_single_punch_frame(
            ax_single, phase, progress,
            defects, hardness, force_kN, excipient
        )
        
        # วาด rotary
        draw_rotary_frame(
            ax_rotary, rotation,
            defects, hardness, speed, excipient
        )
        
        rotation = (rotation + speed / 10) % 360
        
        plt.tight_layout(pad=0.5)
        placeholder.pyplot(fig)
        plt.close()
        
        time.sleep(0.05)