"""
Pharmaceutical Tablet Compression Simulator
Single Punch Press 2D Animation v1.0
Author: Tok
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import time

C = {
    "bg":           "#F8F9FA",
    "machine":      "#E0E0E0",
    "machine_edge": "#424242",
    "accent":       "#1565C0",
    "pipe":         "#212121",
    "powder":       "#F5F5DC",
    "tablet_ok":    "#4CAF50",
    "tablet_bad":   "#FF5722",
    "tablet_lam":   "#FF9800",
    "tablet_twin":  "#9C27B0",
    "text":         "#212121",
    "ok":           "#4CAF50",
    "warning":      "#FF5722",
    "barrel":       "#795548",
    "bucket":       "#F44336",
    "punch":        "#1565C0",
    "punch_edge":   "#90CAF9",
    "die":          "#37474F",
}

# ============================================================
# HELPER
# ============================================================

def draw_label(ax, x, y, text,
               arrow_dx=0, arrow_dy=0,
               color="#388E3C", bg="#E8F5E9"):
    ax.annotate(
        text,
        xy=(x+arrow_dx, y+arrow_dy),
        xytext=(x, y),
        fontsize=7,
        color=C["text"],
        bbox=dict(boxstyle="round,pad=0.3",
                  facecolor=bg,
                  edgecolor=color,
                  linewidth=1),
        arrowprops=dict(arrowstyle="-",
                        color=color, lw=1)
    )

# ============================================================
# COMPONENTS
# ============================================================

def draw_hopper(ax, x, y, frame=0):
    """วาด Powder Hopper"""
    
    # Hopper body
    hopper = patches.Polygon(
        [[x-1.5, y+3], [x+1.5, y+3],
         [x+0.6, y], [x-0.6, y]],
        facecolor="#B0BEC5",
        edgecolor=C["machine_edge"],
        linewidth=2
    )
    ax.add_patch(hopper)
    
    # Powder inside
    powder_fill = patches.Polygon(
        [[x-1.2, y+2.8], [x+1.2, y+2.8],
         [x+0.5, y+0.3], [x-0.5, y+0.3]],
        facecolor=C["powder"],
        alpha=0.7
    )
    ax.add_patch(powder_fill)
    
    # Agitator (แกนกวน)
    angle = np.radians(frame * 8)
    ax.plot(
        [x + 0.6*np.cos(angle), x - 0.6*np.cos(angle)],
        [y + 2 + 0.2*np.sin(angle),
         y + 2 - 0.2*np.sin(angle)],
        color=C["machine_edge"],
        linewidth=2
    )
    
    # Outlet gate
    gate = patches.Rectangle(
        (x-0.3, y-0.2), 0.6, 0.2,
        facecolor=C["machine_edge"]
    )
    ax.add_patch(gate)
    
    # Powder falling
    for i in range(3):
        t = (frame + i*5) % 15
        py = y - 0.4 - t*0.15
        if py > y - 2.5:
            ax.plot(x, py, 'o',
                   color=C["powder"],
                   markersize=3, alpha=0.7)
    
    draw_label(ax, x-3.5, y+3,
               "Powder\nHopper",
               arrow_dx=2, arrow_dy=0,
               color="#455A64", bg="#ECEFF1")


def draw_feed_frame(ax, x, y):
    """วาด Feed Frame (ส่วนป้อนผง)"""
    
    frame_body = patches.Rectangle(
        (x-1.2, y-0.5), 2.4, 1,
        facecolor="#90A4AE",
        edgecolor=C["machine_edge"],
        linewidth=1.5
    )
    ax.add_patch(frame_body)
    
    # Scraper blade
    ax.plot([x-0.8, x+0.8], [y, y],
            color=C["machine_edge"],
            linewidth=2)
    
    draw_label(ax, x+2, y,
               "Feed Frame",
               arrow_dx=-0.8, arrow_dy=0,
               color="#455A64", bg="#ECEFF1")


def draw_die_table(ax, x, y, punch_y, 
                   phase, progress, defects):
    """วาด Die + Punch ส่วนหลัก"""
    
    tablet_color = C["tablet_bad"] if defects.get("capping") else \
                   C["tablet_lam"] if defects.get("lamination") else \
                   C["tablet_twin"] if defects.get("twinning") else \
                   C["tablet_ok"]
    
    # ===== DIE TABLE =====
    table = patches.Rectangle(
        (x-3, y-0.5), 6, 1,
        facecolor="#78909C",
        edgecolor=C["machine_edge"],
        linewidth=2
    )
    ax.add_patch(table)
    
    # Die hole
    die = patches.Rectangle(
        (x-0.8, y-0.5), 1.6, 1,
        facecolor=C["die"],
        edgecolor=C["machine_edge"],
        linewidth=1.5
    )
    ax.add_patch(die)
    
    # ===== LOWER PUNCH =====
    lower_y = y - 0.5
    lower = patches.FancyBboxPatch(
        (x-0.6, lower_y-1.5), 1.2, 1.5,
        boxstyle="round,pad=0.05",
        facecolor=C["punch"],
        edgecolor=C["punch_edge"],
        linewidth=1.5
    )
    ax.add_patch(lower)
    
    # Lower punch rod
    ax.plot([x, x], [lower_y-1.5, lower_y-3],
            color=C["accent"], linewidth=3)
    
    # ===== UPPER PUNCH (เคลื่อนที่ตาม phase) =====
    if phase == 0:
        # Filling: punch อยู่บน
        up_y = y + 3
    elif phase == 1:
        # Compression: punch กดลง
        up_y = y + 3 - progress * 2.8
    else:
        # Ejection: punch ขึ้น
        up_y = y + 0.2 + progress * 2.8
    
    upper = patches.FancyBboxPatch(
        (x-0.6, up_y), 1.2, 1.5,
        boxstyle="round,pad=0.05",
        facecolor=C["punch"],
        edgecolor=C["punch_edge"],
        linewidth=1.5
    )
    ax.add_patch(upper)
    
    # Upper punch rod
    ax.plot([x, x], [up_y+1.5, up_y+4],
            color=C["accent"], linewidth=3)
    
    # ===== POWDER / TABLET in die =====
    if phase == 0:
        # Filling phase
        powder_h = progress * 0.8
        if powder_h > 0:
            powder = patches.Rectangle(
                (x-0.7, y-0.4), 1.4, powder_h,
                facecolor=C["powder"], alpha=0.8
            )
            ax.add_patch(powder)
    
    elif phase == 1:
        # Compression phase
        powder_h = 0.8 - progress * 0.5
        powder = patches.Rectangle(
            (x-0.7, y-0.4), 1.4, max(powder_h, 0.1),
            facecolor=C["powder"], alpha=0.9
        )
        ax.add_patch(powder)
    
    elif phase == 2:
        # Ejection phase
        tablet_y = y - 0.3 + progress * 0.8
        
        if defects.get("capping"):
            # หัวแยก
            body = patches.FancyBboxPatch(
                (x-0.6, tablet_y), 1.2, 0.25,
                boxstyle="round,pad=0.02",
                facecolor=tablet_color, alpha=0.9
            )
            cap = patches.FancyBboxPatch(
                (x-0.6, tablet_y+0.35+progress*0.2),
                1.2, 0.1,
                boxstyle="round,pad=0.02",
                facecolor=tablet_color, alpha=0.6
            )
            ax.add_patch(body)
            ax.add_patch(cap)
        
        elif defects.get("twinning") and progress > 0.5:
            # 2 เม็ดติดกัน
            t1 = plt.Circle((x-0.35, tablet_y+0.2),
                            0.3, facecolor=tablet_color, alpha=0.9)
            t2 = plt.Circle((x+0.35, tablet_y+0.2),
                            0.3, facecolor=tablet_color, alpha=0.9)
            ax.add_patch(t1)
            ax.add_patch(t2)
        
        elif defects.get("lamination"):
            # แตกเป็นชั้น
            for layer in range(3):
                lam = patches.FancyBboxPatch(
                    (x-0.6,
                     tablet_y+layer*0.15+progress*layer*0.05),
                    1.2, 0.1,
                    boxstyle="round,pad=0.01",
                    facecolor=tablet_color,
                    alpha=0.8-layer*0.15
                )
                ax.add_patch(lam)
        
        else:
            tablet = patches.FancyBboxPatch(
                (x-0.6, tablet_y), 1.2, 0.35,
                boxstyle="round,pad=0.05",
                facecolor=tablet_color,
                edgecolor="white", linewidth=1,
                alpha=0.95
            )
            ax.add_patch(tablet)
    
    draw_label(ax, x+2.5, y+2,
               "Upper Punch",
               arrow_dx=-1.5, arrow_dy=-0.8,
               color=C["accent"], bg="#E3F2FD")
    
    draw_label(ax, x+2.5, y-1,
               "Die",
               arrow_dx=-1.5, arrow_dy=0.3,
               color="#455A64", bg="#ECEFF1")
    
    draw_label(ax, x+2.5, y-2.5,
               "Lower Punch",
               arrow_dx=-1.5, arrow_dy=0.8,
               color=C["accent"], bg="#E3F2FD")


def draw_cam_track(ax, x, y, phase, progress):
    """วาด Cam Track (กลไก cam ควบคุม punch)"""
    
    # Cam body
    cam = patches.Ellipse(
        (x, y), 2, 1.5,
        facecolor="#546E7A",
        edgecolor=C["machine_edge"],
        linewidth=1.5,
        alpha=0.7
    )
    ax.add_patch(cam)
    
    # Cam rotation indicator
    cam_angle = np.radians(phase*120 + progress*120)
    ax.plot(
        [x, x + 0.7*np.cos(cam_angle)],
        [y, y + 0.5*np.sin(cam_angle)],
        color=C["punch_edge"],
        linewidth=2
    )
    
    draw_label(ax, x-3, y,
               "Cam\nTrack",
               arrow_dx=1, arrow_dy=0,
               color="#455A64", bg="#ECEFF1")


def draw_tablet_chute(ax, x, y, defects):
    """วาด Tablet Chute (รางเม็ดยา)"""
    
    tablet_color = C["tablet_bad"] \
        if not defects.get("ok", True) \
        else C["tablet_ok"]
    
    # Chute ramp
    chute = patches.Polygon(
        [[x, y], [x+2.5, y],
         [x+3, y-1.5], [x+0.5, y-1.5]],
        facecolor="#90A4AE",
        edgecolor=C["machine_edge"],
        linewidth=1.5
    )
    ax.add_patch(chute)
    
    # Tablet on chute
    tab = plt.Circle(
        (x+1.5, y-0.7), 0.25,
        facecolor=tablet_color,
        edgecolor="white", linewidth=1
    )
    ax.add_patch(tab)
    
    draw_label(ax, x+3.5, y,
               "Tablet\nChute",
               arrow_dx=-0.5, arrow_dy=-0.5,
               color="#455A64", bg="#ECEFF1")


def draw_collection_bin(ax, x, y, 
                         tablet_count=0, defects=None):
    """วาด Collection Bin"""
    
    if defects is None:
        defects = {"ok": True}
    
    tablet_color = C["tablet_bad"] \
        if not defects.get("ok", True) \
        else C["tablet_ok"]
    
    # Bin
    bin_shape = patches.FancyBboxPatch(
        (x-1.5, y-2.5), 3, 3,
        boxstyle="round,pad=0.1",
        facecolor=C["barrel"],
        edgecolor=C["machine_edge"],
        linewidth=2,
        alpha=0.9
    )
    ax.add_patch(bin_shape)
    
    # Fill level
    fill_h = min(tablet_count/50*2.5, 2.5)
    if fill_h > 0:
        fill = patches.Rectangle(
            (x-1.4, y-2.4), 2.8, fill_h,
            facecolor=tablet_color, alpha=0.4
        )
        ax.add_patch(fill)
    
    ax.text(x, y-1,
            f"{tablet_count}\ntablets",
            ha='center', va='center',
            color="white",
            fontsize=8, fontweight='bold')
    
    draw_label(ax, x-3.5, y,
               "Collection\nBin",
               arrow_dx=2, arrow_dy=0,
               color=C["barrel"], bg="#EFEBE9")


def draw_force_gauge(ax, x, y, force_kN, hardness):
    """วาด Force Gauge"""
    
    # Gauge circle
    gauge = plt.Circle(
        (x, y), 1.2,
        facecolor="white",
        edgecolor=C["machine_edge"],
        linewidth=2
    )
    ax.add_patch(gauge)
    
    # Gauge markings
    for i in range(9):
        angle = np.radians(220 - i*27.5)
        ax.plot(
            [x + 0.9*np.cos(angle),
             x + 1.1*np.cos(angle)],
            [y + 0.9*np.sin(angle),
             y + 1.1*np.sin(angle)],
            color=C["machine_edge"],
            linewidth=1
        )
    
    # Needle
    force_pct = min(force_kN / 100, 1.0)
    needle_angle = np.radians(220 - force_pct*220)
    needle_color = "#FF5722" if force_pct > 0.8 else \
                   "#FF9800" if force_pct > 0.5 else "#4CAF50"
    ax.plot(
        [x, x + 0.8*np.cos(needle_angle)],
        [y, y + 0.8*np.sin(needle_angle)],
        color=needle_color, linewidth=2
    )
    ax.plot(x, y, 'o',
            color=C["machine_edge"],
            markersize=5)
    
    ax.text(x, y-0.5,
            f"{force_kN:.0f}kN",
            ha='center', va='center',
            color=C["text"],
            fontsize=7, fontweight='bold')
    
    draw_label(ax, x-2.5, y+1,
               "Force\nGauge",
               arrow_dx=1.3, arrow_dy=-0.3,
               color="#455A64", bg="#ECEFF1")


def draw_machine_body(ax, x, y):
    """วาด Machine Body ภายนอก"""
    
    # Main cabinet
    cabinet = patches.FancyBboxPatch(
        (x-4, y-8), 8, 12,
        boxstyle="round,pad=0.2",
        facecolor="#CFD8DC",
        edgecolor=C["machine_edge"],
        linewidth=2.5,
        alpha=0.3,
        zorder=0
    )
    ax.add_patch(cabinet)
    
    # Legs
    for lx in [x-3.5, x+3.5]:
        leg = patches.Rectangle(
            (lx-0.3, y-9), 0.6, 1,
            facecolor=C["machine_edge"]
        )
        ax.add_patch(leg)
    
    # Machine label
    ax.text(x, y+4.5,
            "Single Punch Press",
            ha='center', va='center',
            color=C["accent"],
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3",
                     facecolor="white",
                     edgecolor=C["accent"],
                     linewidth=1.5)
            )


def draw_single_punch_2d(ax, frame=0,
                          phase=0, progress=0.0,
                          hardness=150, force_kN=10,
                          speed=30, defects=None,
                          tablet_count=0):
    """
    วาด Single Punch 2D diagram ทั้งหมด
    """
    
    if defects is None:
        defects = {"ok": True}
    
    ax.clear()
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 18)
    ax.set_facecolor(C["bg"])
    ax.axis('off')
    
    # Title
    ax.text(10, 17.3,
            "Single Punch Tablet Press & Supportive Devices",
            ha='center', va='center',
            color=C["accent"],
            fontsize=11, fontweight='bold')
    
    center_x = 10
    center_y = 9
    
    # Machine body (background)
    draw_machine_body(ax, center_x, center_y)
    
    # Hopper (top)
    draw_hopper(ax, center_x, 15, frame)
    
    # Feed frame
    draw_feed_frame(ax, center_x, 12.5)
    
    # Cam track
    draw_cam_track(ax, center_x-5, center_y, phase, progress)
    
    # Force gauge
    draw_force_gauge(ax, center_x+6, center_y+2,
                     force_kN if phase == 1 else 0,
                     hardness)
    
    # Die + Punch (หัวใจ)
    draw_die_table(ax, center_x, center_y,
                   center_y, phase, progress, defects)
    
    # Tablet chute
    draw_tablet_chute(ax, center_x+0.8, center_y-2, defects)
    
    # Collection bin
    draw_collection_bin(ax, center_x+5, center_y-4,
                        tablet_count, defects)
    
    # Floor
    floor = patches.Rectangle(
        (0.5, 0.5), 19, 0.4,
        facecolor="#455A64",
        edgecolor=C["machine_edge"]
    )
    ax.add_patch(floor)
    ax.text(10, 0.7, "Ground / Floor",
            ha='center', va='center',
            color="white", fontsize=7)
    
    # ===== PHASE INDICATOR =====
    phase_labels = ["📥 Filling", "⚡ Compression", "📤 Ejection"]
    phase_colors = ["#2196F3", "#FF5722", "#4CAF50"]
    
    for i, (label, color) in enumerate(
            zip(phase_labels, phase_colors)):
        alpha = 1.0 if i == phase else 0.3
        box = patches.FancyBboxPatch(
            (1+i*3.5, 1.2), 3, 0.8,
            boxstyle="round,pad=0.1",
            facecolor=color, alpha=alpha
        )
        ax.add_patch(box)
        ax.text(2.5+i*3.5, 1.6, label,
                ha='center', va='center',
                color="white", fontsize=7,
                fontweight='bold' if i == phase else 'normal')
    
    # ===== STATUS =====
    status_color = C["ok"] if defects.get("ok", True) \
                   else C["warning"]
    defect_name = "Normal ✅" if defects.get("ok", True) else \
                  "CAPPING ⚠️" if defects.get("capping") else \
                  "LAMINATION ⚠️" if defects.get("lamination") else \
                  "STICKING ⚠️" if defects.get("sticking") else \
                  "TWINNING ⚠️"
    
    status_box = patches.FancyBboxPatch(
        (12.5, 1.2), 7, 1.5,
        boxstyle="round,pad=0.2",
        facecolor="white",
        edgecolor=status_color,
        linewidth=2
    )
    ax.add_patch(status_box)
    
    ax.text(16, 2.2,
            f"Status: {defect_name}",
            ha='center', color=status_color,
            fontsize=8, fontweight='bold')
    ax.text(16, 1.7,
            f"Hardness: {hardness:.1f} N | "
            f"Speed: {speed} rpm",
            ha='center', color=C["text"], fontsize=7)


# ============================================================
# STREAMLIT INTEGRATION
# ============================================================

def run_single_punch_2d(hardness, defects,
                         force_kN, speed,
                         placeholder, n_cycles=2):
    """รัน Single Punch animation ใน Streamlit"""
    
    tablet_count = 0
    
    for cycle in range(n_cycles):
        for frame in range(60):
            
            if frame < 20:
                phase    = 0
                progress = frame / 20
            elif frame < 40:
                phase    = 1
                progress = (frame-20) / 20
            else:
                phase    = 2
                progress = (frame-40) / 20
                if progress > 0.8:
                    tablet_count += 1
            
            fig, ax = plt.subplots(figsize=(14, 10))
            fig.patch.set_facecolor(C["bg"])
            
            draw_single_punch_2d(
                ax,
                frame        = frame + cycle*60,
                phase        = phase,
                progress     = progress,
                hardness     = hardness,
                force_kN     = force_kN,
                speed        = speed,
                defects      = defects,
                tablet_count = tablet_count
            )
            
            plt.tight_layout()
            placeholder.pyplot(fig)
            plt.close()
            
            time.sleep(0.06)