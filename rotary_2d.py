"""
Pharmaceutical Tablet Compression Simulator
Rotary Press 2D Animation v1.0
Author: Tok
Reference: Rotary Tablet Press & Supportive Devices diagram
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import numpy as np
import time

# ============================================================
# COLORS
# ============================================================

C = {
    "bg":           "#F8F9FA",
    "machine":      "#E0E0E0",
    "machine_edge": "#424242",
    "accent":       "#1565C0",
    "pipe":         "#212121",
    "powder":       "#F5F5DC",
    "tablet_ok":    "#4CAF50",
    "tablet_bad":   "#FF5722",
    "text":         "#212121",
    "label_bg":     "#E8F5E9",
    "label_edge":   "#388E3C",
    "warning":      "#FF5722",
    "ok":           "#4CAF50",
    "dust":         "#BDBDBD",
    "barrel":       "#795548",
    "bucket":       "#F44336",
}

# ============================================================
# DRAW FUNCTIONS — แต่ละ component
# ============================================================

def draw_label(ax, x, y, text, 
               arrow_dx=0, arrow_dy=0,
               color="#388E3C", bg="#E8F5E9"):
    """วาด label แบบ engineering diagram"""
    ax.annotate(
        text,
        xy=(x + arrow_dx, y + arrow_dy),
        xytext=(x, y),
        fontsize=7,
        color=C["text"],
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor=bg,
            edgecolor=color,
            linewidth=1
        ),
        arrowprops=dict(
            arrowstyle="-",
            color=color,
            lw=1
        )
    )


def draw_vacuum_loader(ax, x, y):
    """วาด Vacuum Loader ด้านบน"""
    
    # Funnel shape
    funnel = patches.Polygon(
        [[x-1.5, y+2], [x+1.5, y+2],
         [x+0.8, y], [x-0.8, y]],
        facecolor=C["machine"],
        edgecolor=C["machine_edge"],
        linewidth=1.5
    )
    ax.add_patch(funnel)
    
    # Motor box
    motor = patches.Rectangle(
        (x-0.5, y+2), 1, 0.8,
        facecolor=C["accent"],
        edgecolor=C["machine_edge"],
        linewidth=1.5
    )
    ax.add_patch(motor)
    
    # Pipe ด้านขวา (vacuum pipe)
    pipe_x = [x+1.5, x+2.5, x+2.5]
    pipe_y = [y+2.5, y+2.5, y-8]
    ax.plot(pipe_x, pipe_y,
            color=C["pipe"],
            linewidth=4,
            solid_capstyle='round')
    
    # Powder particles falling
    for i in range(3):
        ax.plot(x - 0.2 + i*0.2,
                y - 0.3 - i*0.4,
                'o',
                color=C["powder"],
                markersize=4,
                alpha=0.7)
    
    draw_label(ax, x-3.5, y+2.5,
               "Vacuum Loader",
               arrow_dx=2, arrow_dy=0)


def draw_tableting_machine(ax, x, y, 
                            rotation_angle=0,
                            hardness=150,
                            defects=None):
    """วาด Tableting Machine — หัวใจของ simulator"""
    
    if defects is None:
        defects = {"ok": True}
    
    # ===== MACHINE BODY =====
    body = patches.Rectangle(
        (x-2.5, y-6), 5, 9,
        facecolor=C["machine"],
        edgecolor=C["machine_edge"],
        linewidth=2
    )
    ax.add_patch(body)
    
    # ===== TURRET (top view แบบ side) =====
    turret = patches.Ellipse(
        (x, y+1), 4, 2,
        facecolor="#90A4AE",
        edgecolor=C["machine_edge"],
        linewidth=2
    )
    ax.add_patch(turret)
    
    # ===== 16 PUNCH HOLES =====
    n = 8  # แสดงแค่ด้านหน้า
    for i in range(n):
        px = x - 1.8 + i * 0.5
        py = y + 0.9
        
        # เช็ค defect
        if defects.get("capping") and i == 3:
            color = C["tablet_bad"]
        elif defects.get("twinning") and i == 5:
            color = C["tablet_bad"]
        else:
            color = C["accent"]
        
        punch_hole = plt.Circle(
            (px, py), 0.15,
            facecolor=color,
            edgecolor=C["machine_edge"],
            linewidth=1
        )
        ax.add_patch(punch_hole)
    
    # ===== CONTROL PANEL =====
    panel = patches.Rectangle(
        (x+0.5, y-2), 1.5, 2.5,
        facecolor="#37474F",
        edgecolor=C["machine_edge"],
        linewidth=1
    )
    ax.add_patch(panel)
    
    # Screen on panel
    screen = patches.Rectangle(
        (x+0.6, y-1.5), 1.3, 1.5,
        facecolor="#1565C0",
        edgecolor="#90CAF9",
        linewidth=1
    )
    ax.add_patch(screen)
    
    # Hardness indicator on screen
    hardness_color = C["ok"] if 40 <= hardness <= 200 \
                     else C["warning"]
    ax.text(x+1.25, y-0.8,
            f"{hardness:.0f}N",
            ha='center', va='center',
            color=hardness_color,
            fontsize=6, fontweight='bold')
    
    # ===== BUTTONS =====
    for i, btn_color in enumerate(['#4CAF50', '#FF5722', '#FF9800']):
        btn = plt.Circle(
            (x+0.8+i*0.4, y-1.8), 0.1,
            facecolor=btn_color,
            edgecolor="white",
            linewidth=0.5
        )
        ax.add_patch(btn)
    
    # ===== LEGS =====
    for lx in [x-2, x+2]:
        leg = patches.Rectangle(
            (lx-0.2, y-7.5), 0.4, 1.5,
            facecolor=C["machine_edge"],
            edgecolor=C["machine_edge"]
        )
        ax.add_patch(leg)
    
    # ===== OUTLET (tablet ออกมา) =====
    outlet = patches.FancyArrowPatch(
        (x-2.5, y-3), (x-4, y-3),
        arrowstyle='-|>',
        color=C["accent"],
        linewidth=2,
        mutation_scale=15
    )
    ax.add_patch(outlet)
    
    draw_label(ax, x-3.5, y+2,
               "Tableting\nMachine",
               arrow_dx=1, arrow_dy=-1)


def draw_screening_machine(ax, x, y, defects=None):
    """วาด Screening Machine"""
    
    if defects is None:
        defects = {"ok": True}
    
    # Body
    screen_body = patches.Rectangle(
        (x-1.5, y-2), 3, 3.5,
        facecolor=C["machine"],
        edgecolor=C["machine_edge"],
        linewidth=1.5
    )
    ax.add_patch(screen_body)
    
    # Screen mesh
    for i in range(4):
        ax.plot(
            [x-1.3, x+1.3],
            [y-1.5+i*0.5, y-1.5+i*0.5],
            color=C["machine_edge"],
            linewidth=0.5,
            alpha=0.5
        )
    
    # Vibration springs
    for sx in [x-1.2, x+1.2]:
        for sy in [y-2.2, y-2.5, y-2.8]:
            ax.plot(
                [sx-0.1, sx+0.1],
                [sy, sy-0.1],
                color=C["machine_edge"],
                linewidth=1
            )
    
    # Outlet ดี → finished barrel
    good_arrow = patches.FancyArrowPatch(
        (x-1.5, y-1), (x-3, y-1),
        arrowstyle='-|>',
        color=C["ok"],
        linewidth=1.5,
        mutation_scale=12
    )
    ax.add_patch(good_arrow)
    
    # Outlet เสีย → rejection bucket
    bad_arrow = patches.FancyArrowPatch(
        (x, y-2), (x, y-3.5),
        arrowstyle='-|>',
        color=C["warning"],
        linewidth=1.5,
        mutation_scale=12
    )
    ax.add_patch(bad_arrow)
    
    draw_label(ax, x+2, y+1.5,
               "Screening\nMachine",
               arrow_dx=-0.5, arrow_dy=-0.5)


def draw_finished_barrel(ax, x, y, tablet_count=0):
    """วาด Finished Barrel"""
    
    # Barrel body
    barrel = patches.FancyBboxPatch(
        (x-1.2, y-2.5), 2.4, 3,
        boxstyle="round,pad=0.1",
        facecolor=C["barrel"],
        edgecolor=C["machine_edge"],
        linewidth=1.5,
        alpha=0.8
    )
    ax.add_patch(barrel)
    
    # Barrel bands
    for by in [y-1.5, y-0.5]:
        band = patches.Rectangle(
            (x-1.2, by), 2.4, 0.15,
            facecolor="#4E342E",
            edgecolor=C["machine_edge"],
            linewidth=0.5
        )
        ax.add_patch(band)
    
    # Tablets inside (แสดง fill level)
    fill_h = min(tablet_count / 100 * 2.5, 2.5)
    if fill_h > 0:
        fill = patches.Rectangle(
            (x-1.1, y-2.4), 2.2, fill_h,
            facecolor=C["tablet_ok"],
            alpha=0.4
        )
        ax.add_patch(fill)
    
    ax.text(x, y-1,
            f"{tablet_count}\ntablets",
            ha='center', va='center',
            color="white",
            fontsize=7, fontweight='bold')
    
    draw_label(ax, x-3, y-1,
               "Finished\nBarrel",
               arrow_dx=1.8, arrow_dy=0,
               color="#795548", bg="#EFEBE9")


def draw_rejection_bucket(ax, x, y, reject_count=0):
    """วาด Rejection Bucket"""
    
    # Bucket
    bucket = patches.Polygon(
        [[x-0.8, y+0.5], [x+0.8, y+0.5],
         [x+1, y-1.5], [x-1, y-1.5]],
        facecolor=C["bucket"],
        edgecolor=C["machine_edge"],
        linewidth=1.5,
        alpha=0.8
    )
    ax.add_patch(bucket)
    
    # Handle
    handle = patches.Arc(
        (x, y+0.5), 0.8, 0.5,
        theta1=0, theta2=180,
        color=C["machine_edge"],
        linewidth=1.5
    )
    ax.add_patch(handle)
    
    if reject_count > 0:
        ax.text(x, y-0.5,
                f"❌ {reject_count}",
                ha='center', va='center',
                color="white",
                fontsize=7, fontweight='bold')
    
    draw_label(ax, x+1.5, y,
               "Rejection\nBucket",
               arrow_dx=-0.5, arrow_dy=0,
               color="#C62828", bg="#FFEBEE")


def draw_vacuum_dedustor(ax, x, y):
    """วาด Vacuum Dedustor"""
    
    # Body
    body = patches.Rectangle(
        (x-1, y-2), 2, 3,
        facecolor=C["machine"],
        edgecolor=C["machine_edge"],
        linewidth=1.5
    )
    ax.add_patch(body)
    
    # Filter indicator
    for i in range(3):
        filt = patches.Rectangle(
            (x-0.7, y-1.5+i*0.6), 1.4, 0.3,
            facecolor=C["dust"],
            edgecolor=C["machine_edge"],
            linewidth=0.5
        )
        ax.add_patch(filt)
    
    # Pipe connection
    ax.plot(
        [x-1, x-2.5],
        [y+0.5, y+0.5],
        color=C["pipe"],
        linewidth=3,
        solid_capstyle='round'
    )
    
    # Dust collection
    dust_box = patches.Rectangle(
        (x-0.8, y-2.8), 1.6, 0.8,
        facecolor=C["dust"],
        edgecolor=C["machine_edge"],
        linewidth=1
    )
    ax.add_patch(dust_box)
    
    draw_label(ax, x+1.5, y+1.5,
               "Vacuum\nDedustor",
               arrow_dx=-0.5, arrow_dy=-0.5)


def draw_floor(ax, x_min, x_max, y):
    """วาด Floor/Ground"""
    
    # Floor
    floor = patches.Rectangle(
        (x_min, y-0.5), x_max-x_min, 0.5,
        facecolor="#455A64",
        edgecolor=C["machine_edge"],
        linewidth=1
    )
    ax.add_patch(floor)
    
    # Hatching
    for i in range(int((x_max-x_min)/0.8)):
        fx = x_min + i*0.8
        ax.plot(
            [fx, fx+0.4],
            [y-0.5, y-0.8],
            color=C["machine_edge"],
            linewidth=0.8,
            alpha=0.5
        )
    
    ax.text((x_min+x_max)/2, y-0.3,
            "Ground / Floor",
            ha='center', va='center',
            color="white",
            fontsize=7)

# ============================================================
# POWDER FLOW ANIMATION
# ============================================================

def draw_powder_particles(ax, frame, defects):
    """วาด powder particles ไหลในระบบ"""
    
    # Particles จาก vacuum loader ลงมา
    for i in range(3):
        t = (frame + i*7) % 20
        py = 14 - t * 0.5
        if py > 7:
            ax.plot(10, py, 'o',
                   color=C["powder"],
                   markersize=3,
                   alpha=0.6)
    
    # Tablets ออกจากเครื่อง
    tablet_color = C["tablet_bad"] if not defects.get("ok", True) \
                   else C["tablet_ok"]
    
    for i in range(2):
        t = (frame + i*10) % 20
        tx = 8 - t * 0.15
        if 4 < tx < 8:
            ax.plot(tx, 10,
                   's',
                   color=tablet_color,
                   markersize=5,
                   alpha=0.8)

# ============================================================
# MAIN DRAW FUNCTION
# ============================================================

def draw_rotary_2d(ax, frame=0, rotation_angle=0,
                   hardness=150, defects=None,
                   tablet_count=0, reject_count=0):
    """
    วาด Rotary Press 2D diagram ทั้งหมด
    ตาม reference image
    """
    
    if defects is None:
        defects = {"ok": True}
    
    ax.clear()
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 18)
    ax.set_facecolor(C["bg"])
    ax.axis('off')
    
    # Title
    ax.text(11, 17.3,
            "Rotary Tablet Press & Supportive Devices",
            ha='center', va='center',
            color=C["accent"],
            fontsize=11, fontweight='bold')
    
    # ===== DRAW ALL COMPONENTS =====
    
    # Vacuum Loader (top center)
    draw_vacuum_loader(ax, 10, 15)
    
    # Tableting Machine (center)
    draw_tableting_machine(
        ax, 10, 12,
        rotation_angle=rotation_angle,
        hardness=hardness,
        defects=defects
    )
    
    # Screening Machine (left of tableting)
    draw_screening_machine(ax, 5, 10, defects)
    
    # Finished Barrel (far left)
    draw_finished_barrel(ax, 2, 8.5, tablet_count)
    
    # Rejection Bucket (below screening)
    draw_rejection_bucket(ax, 5, 6.5, reject_count)
    
    # Vacuum Dedustor (right)
    draw_vacuum_dedustor(ax, 17, 10)
    
    # Floor
    draw_floor(ax, 0.5, 21.5, 4.5)
    
    # Powder particles animation
    draw_powder_particles(ax, frame, defects)
    
    # ===== STATUS BOX =====
    status_color = C["ok"] if defects.get("ok", True) \
                   else C["warning"]
    status_text = "✅ Normal Operation" if defects.get("ok", True) \
                  else "⚠️ " + (
                      "CAPPING" if defects.get("capping") else
                      "LAMINATION" if defects.get("lamination") else
                      "STICKING" if defects.get("sticking") else
                      "TWINNING" if defects.get("twinning") else
                      "DEFECT"
                  )
    
    status_box = patches.FancyBboxPatch(
        (14, 14), 7, 2.5,
        boxstyle="round,pad=0.2",
        facecolor="white",
        edgecolor=status_color,
        linewidth=2
    )
    ax.add_patch(status_box)
    
    ax.text(17.5, 15.8,
            "Status",
            ha='center', color=C["text"],
            fontsize=8, fontweight='bold')
    
    ax.text(17.5, 15.2,
            status_text,
            ha='center', color=status_color,
            fontsize=9, fontweight='bold')
    
    ax.text(17.5, 14.5,
            f"Hardness: {hardness:.1f} N",
            ha='center', color=C["text"],
            fontsize=8)
    
    # ===== ARROWS สำหรับ flow =====
    # Powder flow ลงมาจาก hopper
    ax.annotate('', xy=(10, 13.5), xytext=(10, 14.8),
                arrowprops=dict(arrowstyle='->', 
                               color=C["accent"], lw=1.5))
    
    # Tablet flow ไป screening
    ax.annotate('', xy=(6.5, 10), xytext=(7.5, 10),
                arrowprops=dict(arrowstyle='->',
                               color=C["ok"], lw=1.5))
    
    # Good tablets ไป finished barrel
    ax.annotate('', xy=(3.2, 8.5), xytext=(3.2, 10),
                arrowprops=dict(arrowstyle='->',
                               color=C["ok"], lw=1.5))


# ============================================================
# STREAMLIT INTEGRATION
# ============================================================

def run_rotary_2d_animation(hardness, defects,
                             tablet_count, reject_count,
                             placeholder, n_frames=40):
    """รัน animation ใน Streamlit"""
    
    for frame in range(n_frames):
        
        fig, ax = plt.subplots(figsize=(14, 9))
        fig.patch.set_facecolor(C["bg"])
        
        rotation = (frame * 10) % 360
        
        draw_rotary_2d(
            ax,
            frame        = frame,
            rotation_angle = rotation,
            hardness     = hardness,
            defects      = defects,
            tablet_count = min(frame * 3, tablet_count),
            reject_count = min(frame // 10, reject_count)
        )
        
        plt.tight_layout()
        placeholder.pyplot(fig)
        plt.close()
        
        time.sleep(0.08)