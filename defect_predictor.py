"""
Pharmaceutical Tablet Compression Simulator
Defect Predictor v1.0
Author: Tok
Predicts: Capping, Lamination, Sticking, Twinning
"""

from exipient_database import EXCIPIENT_EXTENDED
from machinemodule import (MACHINES, force_to_pressure, 
                            speed_to_dwell, dwell_time_factor)
from mainproject_physicc_engine import simulate

# ============================================================
# DEFECT THRESHOLDS
# ============================================================
# ค่า threshold ที่ใช้ตัดสินว่า defect จะเกิดไหม
# validate ด้วย literature ทีหลัง

DEFECT_THRESHOLDS = {
    "capping": {
        "hardness_max":    350,   # N (เกินนี้ = risk สูง)
        "speed_max":       50,    # rpm (เกินนี้ = risk สูง)
        "dwell_min":       10,    # ms (น้อยกว่านี้ = risk สูง)
    },
    "lamination": {
        "porosity_max":    0.25,  # (เกินนี้ = air entrapment risk)
        "speed_max":       45,    # rpm
        "compressibility_bad": ["Poor", "Fair"],
    },
    "sticking": {
        "carr_index_max":  30,    # % (เกินนี้ = sticking risk)
        "moisture_sensitive": True,
    },
    "twinning": {
        "speed_max":       50,    # rpm (single punch)
        "hardness_min":    60,    # N (ต่ำกว่านี้ = risk สูง)
    },
}

# ============================================================
# DEFECT PREDICTION FUNCTIONS
# ============================================================

def predict_capping(hardness, speed, dwell_ms):
    """
    Capping Prediction
    
    Pharmacy logic:
    → Capping เกิดเมื่อ elastic recovery ชนะ bonding
    → Hardness สูงเกิน = over-compressed = cap
    → Speed สูง = dwell สั้น = bonding ไม่สมบูรณ์ = cap
    → Dwell สั้น = powder ไม่มีเวลา deform = cap
    """
    
    thresh = DEFECT_THRESHOLDS["capping"]
    risk_score = 0
    reasons = []
    
    if hardness > thresh["hardness_max"]:
        risk_score += 40
        reasons.append(f"Hardness {hardness:.1f} N สูงเกิน {thresh['hardness_max']} N")
    
    if speed > thresh["speed_max"]:
        risk_score += 35
        reasons.append(f"Speed {speed} rpm สูงเกิน {thresh['speed_max']} rpm")
    
    if dwell_ms < thresh["dwell_min"]:
        risk_score += 25
        reasons.append(f"Dwell time {dwell_ms:.1f} ms สั้นเกิน {thresh['dwell_min']} ms")
    
    return risk_score, reasons


def predict_lamination(porosity, speed, excipient_name):
    """
    Lamination Prediction
    
    Pharmacy logic:
    → Lamination เกิดเมื่อ air ถูกกักใน tablet
    → Porosity สูง = มี air มาก = lamination risk
    → Speed สูง = air ไม่มีเวลาออก = lamination
    → Compressibility ไม่ดี = bonding ไม่สม่ำเสมอ
    """
    
    thresh = DEFECT_THRESHOLDS["lamination"]
    risk_score = 0
    reasons = []
    
    if porosity > thresh["porosity_max"]:
        risk_score += 40
        reasons.append(f"Porosity {porosity:.3f} สูงเกิน {thresh['porosity_max']}")
    
    if speed > thresh["speed_max"]:
        risk_score += 30
        reasons.append(f"Speed {speed} rpm สูงเกิน {thresh['speed_max']} rpm")
    
    if excipient_name in EXCIPIENT_EXTENDED:
        exc = EXCIPIENT_EXTENDED[excipient_name]
        if exc["compressibility"] in thresh["compressibility_bad"]:
            risk_score += 30
            reasons.append(f"Compressibility {exc['compressibility']} ไม่ดีพอ")
    
    return risk_score, reasons


def predict_sticking(excipient_name, temperature=25.0):
    """
    Sticking Prediction
    
    Pharmacy logic:
    → Sticking เกิดเมื่อ ยาติด punch
    → Carr index สูง = powder เกาะตัวกันง่าย
    → Moisture sensitive + temperature สูง = sticking risk
    → ต้องเพิ่ม lubricant (Mg stearate)
    """
    
    thresh = DEFECT_THRESHOLDS["sticking"]
    risk_score = 0
    reasons = []
    
    if excipient_name in EXCIPIENT_EXTENDED:
        exc = EXCIPIENT_EXTENDED[excipient_name]
        
        if exc["carr_index"] > thresh["carr_index_max"]:
            risk_score += 40
            reasons.append(f"Carr Index {exc['carr_index']}% สูงเกิน {thresh['carr_index_max']}%")
        
        if exc["moisture_sensitive"] and temperature > 30:
            risk_score += 35
            reasons.append(f"Moisture sensitive + Temperature {temperature}°C สูง")
        
        if exc["hygroscopic"]:
            risk_score += 25
            reasons.append("Excipient hygroscopic = moisture ดูดซึม")
    
    return risk_score, reasons


def predict_twinning(hardness, speed, machine_type="single"):
    """
    Twinning Prediction
    
    Pharmacy logic:
    → Twinning เกิดเมื่อ tablet ออกจากเครื่องไม่สมบูรณ์
    → Speed สูง = ejection เร็วเกิน = tablet ค้าง = twin
    → Hardness ต่ำ = tablet ยังนิ่ม = เกาะกัน
    → Single punch มี risk สูงกว่า rotary
    """
    
    thresh = DEFECT_THRESHOLDS["twinning"]
    risk_score = 0
    reasons = []
    
    speed_limit = thresh["speed_max"] if machine_type == "single" else thresh["speed_max"] * 2
    
    if speed > speed_limit:
        risk_score += 40
        reasons.append(f"Speed {speed} rpm สูงเกิน {speed_limit} rpm")
    
    if hardness < thresh["hardness_min"]:
        risk_score += 35
        reasons.append(f"Hardness {hardness:.1f} N ต่ำกว่า {thresh['hardness_min']} N")
    
    if machine_type == "single":
        risk_score += 10
        reasons.append("Single punch มี twinning risk สูงกว่า rotary")
    
    return risk_score, reasons

# ============================================================
# RISK LEVEL
# ============================================================

def risk_level(score):
    """แปลง score → risk level"""
    if score == 0:
        return "✅ ต่ำมาก"
    elif score <= 25:
        return "🟡 ต่ำ"
    elif score <= 50:
        return "🟠 ปานกลาง"
    elif score <= 75:
        return "🔴 สูง"
    else:
        return "🚨 สูงมาก"

# ============================================================
# FULL DEFECT ANALYSIS
# ============================================================

def full_defect_analysis(excipient_name, force_kN, 
                          speed, machine_type="single",
                          temperature=25.0):
    """
    วิเคราะห์ defect ทั้งหมดในครั้งเดียว
    
    นี่คือ QbD thinking จริงๆ:
    → ไม่ใช่แค่ผ่าน/ไม่ผ่าน
    → แต่รู้ว่า risk อยู่ตรงไหน
    → แก้ปัญหาได้ก่อนผลิตจริง
    """
    
    machine = MACHINES.get(
        "single_punch" if machine_type == "single" else "rotary_16"
    )
    
    # คำนวณค่าพื้นฐาน
    pressure  = force_to_pressure(force_kN, machine["punch_diameter"])
    dwell_ms  = speed_to_dwell(speed, 
                1 if machine_type == "single" else machine["stations"])
    
    result = simulate(excipient_name, pressure)
    if not result:
        return
    
    hardness = result["hardness"] * dwell_time_factor(dwell_ms)
    porosity = result["porosity"]
    
    # Predict ทุก defect
    cap_score,  cap_reasons  = predict_capping(hardness, speed, dwell_ms)
    lam_score,  lam_reasons  = predict_lamination(porosity, speed, excipient_name)
    sti_score,  sti_reasons  = predict_sticking(excipient_name, temperature)
    twin_score, twin_reasons = predict_twinning(hardness, speed, machine_type)
    
    # แสดงผล
    print(f"\n{'='*55}")
    print(f"  Defect Risk Analysis")
    print(f"{'='*55}")
    print(f"  Excipient : {excipient_name}")
    print(f"  Force     : {force_kN} kN → {pressure} MPa")
    print(f"  Speed     : {speed} rpm")
    print(f"  Hardness  : {hardness:.1f} N")
    print(f"  Temp      : {temperature}°C")
    print(f"{'-'*55}")
    
    defects = [
        ("Capping",    cap_score,  cap_reasons),
        ("Lamination", lam_score,  lam_reasons),
        ("Sticking",   sti_score,  sti_reasons),
        ("Twinning",   twin_score, twin_reasons),
    ]
    
    for defect_name, score, reasons in defects:
        level = risk_level(score)
        print(f"\n  {defect_name}: {level} (Score: {score})")
        for r in reasons:
            print(f"    → {r}")
    
    print(f"\n{'='*55}")
    
    # Overall recommendation
    max_score = max(cap_score, lam_score, sti_score, twin_score)
    print(f"  Overall Risk: {risk_level(max_score)}")
    
    if max_score > 50:
        print(f"\n  ⚠️  คำแนะนำ:")
        if cap_score > 50:
            print("  → ลด force หรือลด speed")
        if lam_score > 50:
            print("  → ลด speed หรือเปลี่ยน excipient")
        if sti_score > 50:
            print("  → เพิ่ม lubricant หรือลด temperature")
        if twin_score > 50:
            print("  → ลด speed หรือเพิ่ม hardness")
    else:
        print("  → Process อยู่ในเกณฑ์ปลอดภัย")
    
    print(f"{'='*55}")

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    
    print("="*55)
    print("  Defect Predictor v1.0")
    print("="*55)
    
    from exipient_database import EXCIPIENT_EXTENDED
    print("Excipient ที่มี:", list(EXCIPIENT_EXTENDED.keys()))
    
    exc      = input("Excipient: ").strip()
    force    = float(input("Force (kN): "))
    speed    = float(input("Speed (rpm): "))
    machine  = input("Machine (single/rotary): ").strip()
    temp     = float(input("Temperature (°C): "))
    
    full_defect_analysis(exc, force, speed, machine, temp)