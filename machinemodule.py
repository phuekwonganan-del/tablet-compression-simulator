"""
Pharmaceutical Tablet Compression Simulator
Machine Module v1.0
Author: Tok
Covers: Single Punch Press, Rotary Press
"""

import math
from mainproject_physicc_engine import simulate, EXCIPIENTS

# ============================================================
# MACHINE DATABASE
# ============================================================

MACHINES = {
    "single_punch": {
        "name": "Single Punch Press",
        "max_force": 100,        # kN
        "max_speed": 60,         # tablets/min
        "punch_diameter": 8.0,   # mm
        "type": "single",
    },
    "rotary_16": {
        "name": "Rotary Press 16 stations",
        "max_force": 80,         # kN
        "max_speed": 3000,       # tablets/min
        "punch_diameter": 8.0,   # mm
        "stations": 16,
        "type": "rotary",
    },
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def force_to_pressure(force_kN, diameter_mm):
    """
    แปลง compression force (kN) → pressure (MPa)
    
    Pharmacy logic:
    → เครื่องตอกวัดเป็น kN (kilonewton)
    → Heckel equation ใช้ MPa
    → ต้องแปลงก่อนส่งเข้า physics engine
    
    P = F / A
    A = pi * r^2 (พื้นที่หน้าตัดของ punch)
    """
    radius_m = (diameter_mm / 2) / 1000
    area_m2  = math.pi * radius_m ** 2
    pressure_Pa  = (force_kN * 1000) / area_m2
    pressure_MPa = pressure_Pa / 1e6
    return round(pressure_MPa, 2)


def dwell_time_factor(dwell_ms):
    """
    คำนวณ dwell time factor
    
    Pharmacy logic:
    → Dwell time = เวลาที่ punch กดค้างไว้ (milliseconds)
    → ยิ่งนาน = powder มีเวลา plastic deformation มากขึ้น
    → hardness เพิ่มขึ้นตาม log scale
    → reference dwell time = 20 ms (standard)
    """
    reference_dwell = 20.0
    factor = 1 + 0.1 * math.log(dwell_ms / reference_dwell + 1)
    return round(factor, 4)


def speed_to_dwell(speed_rpm, stations=1):
    """
    แปลง speed → dwell time
    
    Pharmacy logic:
    → Single punch: dwell ขึ้นกับ speed โดยตรง
    → Rotary: dwell ขึ้นกับ speed + จำนวน station
    → ยิ่งเร็ว = dwell time สั้นลง
    """
    if stations == 1:
        dwell_ms = (60 / speed_rpm) * 1000 * 0.1
    else:
        dwell_ms = (60 / (speed_rpm * stations)) * 1000 * 10
    return round(dwell_ms, 2)

# ============================================================
# SINGLE PUNCH SIMULATOR
# ============================================================

def simulate_single_punch(excipient_name, force_kN, 
                           speed_rpm, n_tablets=100):
    """
    Simulate Single Punch Press
    
    Pharmacy logic:
    → Single punch ใช้ใน lab scale
    → ผลิตได้น้อย แต่ควบคุมได้ดี
    → ใช้ทดสอบ formulation ก่อน scale up
    
    Input:
    → excipient_name: ชื่อ excipient
    → force_kN: แรงกด (kN)
    → speed_rpm: ความเร็ว (tablets/min)
    → n_tablets: จำนวนเม็ดที่ต้องการ
    
    Output:
    → tablet properties
    → uniformity
    → throughput
    → QC result
    """
    
    machine = MACHINES["single_punch"]
    
    # เช็ค force ไม่เกิน max
    if force_kN > machine["max_force"]:
        print(f"⚠️ Force เกิน max ({machine['max_force']} kN)")
        return None
    
    # เช็ค speed ไม่เกิน max
    if speed_rpm > machine["max_speed"]:
        print(f"⚠️ Speed เกิน max ({machine['max_speed']} rpm)")
        return None
    
    # แปลงค่า
    pressure  = force_to_pressure(force_kN, machine["punch_diameter"])
    dwell_ms  = speed_to_dwell(speed_rpm)
    dt_factor = dwell_time_factor(dwell_ms)
    
    # คำนวณ tablet properties
    # ใช้ physics engine เดิม + dwell time factor
    result = simulate(excipient_name, pressure)
    if not result:
        return None
    
    # Adjust hardness ตาม dwell time
    adjusted_hardness = result["hardness"] * dt_factor
    
    # คำนวณ uniformity (สมมติ normal distribution)
    # CV% ต่ำ = uniform ดี, สูง = ไม่ uniform
    cv_percent = 2.5 + (speed_rpm / machine["max_speed"]) * 5.0
    
    # คำนวณ throughput
    throughput = speed_rpm  # tablets/min
    time_needed = n_tablets / throughput  # minutes
    
    # QC check
    if 40 <= adjusted_hardness <= 200 and cv_percent <= 5.0:
        qc = "✅ ผ่าน QC"
    elif adjusted_hardness < 40:
        qc = "❌ เม็ดยาอ่อนเกินไป"
    elif adjusted_hardness > 200:
        qc = "❌ เม็ดยาแข็งเกินไป"
    else:
        qc = "❌ Uniformity ไม่ผ่าน (CV > 5%)"
    
    return {
        "machine":           machine["name"],
        "excipient":         excipient_name,
        "force":             force_kN,
        "pressure":          pressure,
        "speed":             speed_rpm,
        "dwell_time":        dwell_ms,
        "dwell_factor":      dt_factor,
        "hardness_base":     round(result["hardness"], 2),
        "hardness_adjusted": round(adjusted_hardness, 2),
        "cv_percent":        round(cv_percent, 2),
        "throughput":        throughput,
        "time_for_batch":    round(time_needed, 2),
        "qc":                qc
    }

# ============================================================
# ROTARY PRESS SIMULATOR
# ============================================================

def simulate_rotary(excipient_name, force_kN, 
                    speed_rpm, n_tablets=10000):
    """
    Simulate Rotary Press
    
    Pharmacy logic:
    → Rotary ใช้ใน production scale
    → ผลิตได้มาก แต่ควบคุมยากกว่า
    → มีหลาย station = หลาย punch ทำงานพร้อมกัน
    → dwell time สั้นกว่า single punch มาก
    """
    
    machine  = MACHINES["rotary_16"]
    stations = machine["stations"]
    
    if force_kN > machine["max_force"]:
        print(f"⚠️ Force เกิน max ({machine['max_force']} kN)")
        return None
    
    # แปลงค่า
    pressure  = force_to_pressure(force_kN, machine["punch_diameter"])
    dwell_ms  = speed_to_dwell(speed_rpm, stations)
    dt_factor = dwell_time_factor(dwell_ms)
    
    # คำนวณ tablet properties
    result = simulate(excipient_name, pressure)
    if not result:
        return None
    
    adjusted_hardness = result["hardness"] * dt_factor
    
    # Rotary มี inter-station variation เพิ่มขึ้น
    cv_percent = 1.5 + (speed_rpm / machine["max_speed"]) * 8.0
    
    # Throughput สูงกว่า single punch มาก
    throughput  = speed_rpm * stations
    time_needed = n_tablets / throughput
    
    if 40 <= adjusted_hardness <= 200 and cv_percent <= 5.0:
        qc = "✅ ผ่าน QC"
    elif adjusted_hardness < 40:
        qc = "❌ เม็ดยาอ่อนเกินไป"
    elif adjusted_hardness > 200:
        qc = "❌ เม็ดยาแข็งเกินไป"
    else:
        qc = "❌ Uniformity ไม่ผ่าน (CV > 5%)"
    
    return {
        "machine":           machine["name"],
        "excipient":         excipient_name,
        "force":             force_kN,
        "pressure":          pressure,
        "speed":             speed_rpm,
        "stations":          stations,
        "dwell_time":        dwell_ms,
        "dwell_factor":      dt_factor,
        "hardness_base":     round(result["hardness"], 2),
        "hardness_adjusted": round(adjusted_hardness, 2),
        "cv_percent":        round(cv_percent, 2),
        "throughput":        throughput,
        "time_for_batch":    round(time_needed, 2),
        "qc":                qc
    }

# ============================================================
# PRINT RESULT
# ============================================================

def print_machine_result(result):
    print("\n" + "="*50)
    print(f"  {result['machine']}")
    print("="*50)
    print(f"  Excipient    : {result['excipient']}")
    print(f"  Force        : {result['force']} kN")
    print(f"  Pressure     : {result['pressure']} MPa")
    print(f"  Speed        : {result['speed']} rpm")
    print(f"  Dwell Time   : {result['dwell_time']} ms")
    print("-"*50)
    print(f"  Hardness     : {result['hardness_adjusted']} N")
    print(f"  Uniformity   : CV = {result['cv_percent']} %")
    print(f"  Throughput   : {result['throughput']} tablets/min")
    print(f"  Batch Time   : {result['time_for_batch']} min")
    print("-"*50)
    print(f"  QC Result    : {result['qc']}")
    print("="*50)

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    
    print("="*50)
    print("  Machine Module v1.0")
    print("="*50)
    print("1 = Single Punch Press")
    print("2 = Rotary Press")
    
    mode = input("เลือก (1/2): ")
    
    print("Excipient ที่มี:", list(EXCIPIENTS.keys()))
    exc      = input("Excipient: ").strip()
    force    = float(input("Force (kN): "))
    speed    = float(input("Speed (rpm): "))
    
    if mode == "1":
        result = simulate_single_punch(exc, force, speed)
    elif mode == "2":
        result = simulate_rotary(exc, force, speed)
    else:
        result = None
    
    if result:
        print_machine_result(result)