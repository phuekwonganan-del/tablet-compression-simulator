"""
Pharmaceutical Tablet Compression Simulator
Physics Engine v1.0
Author: Tok
Based on: Heckel, Ryshkewitch-Duckworth, Fell-Newton equations
"""

import math

# ============================================================
# EXCIPIENT DATABASE
# ============================================================
# ออกแบบเป็น dictionary ให้เพิ่มตัวใหม่ได้ง่าย
# แค่เพิ่ม entry ใหม่ ไม่ต้องแก้โค้ดส่วนอื่น


EXCIPIENTS = {
    "MCC_PH102": {
        "name": "Microcrystalline Cellulose PH102",
        "heckel_K": 0.0128,
        "heckel_A": 0.42,
        "max_tensile": 9.5,
        "bonding_b": 6.5,
        "density": 1.512,
    },
    "Lactose_DC": {
        "name": "Lactose Monohydrate DC",
        "heckel_K": 0.0082,      # อัดยากกว่า MCC
        "heckel_A": 0.35,        # initial packing ต่ำกว่า
        "max_tensile": 5.2,      # แรงยึดเกาะน้อยกว่า MCC
        "bonding_b": 5.8,
        "density": 1.545,
    },
    "DCP": {
        "name": "Dicalcium Phosphate Anhydrous",
        "heckel_K": 0.0045,      # อัดยากที่สุดในสาม
        "heckel_A": 0.28,
        "max_tensile": 3.8,
        "bonding_b": 4.2,
        "density": 2.890,
    },

    # เพิ่ม excipient ใหม่ตรงนี้ได้เลย เช่น
    # "Lactose_DC": { ... }
    # "DCP": { ... }
}

# ============================================================
# PHYSICS EQUATIONS
# ============================================================

def heckel(pressure, K, A):
    """
    Heckel Equation: คำนวณ relative density
    
    Pharmacy logic:
    → วัดว่าผงอัดแน่นแค่ไหนภายใต้แรงกด
    → D = 1 หมายถึงอัดแน่น 100% (ไม่มีรูพรุน)
    → D = 0 หมายถึงยังเป็นผงอยู่
    
    K = ความสามารถในการอัด (สูง = อัดง่าย)
    A = การอัดตัวเริ่มต้นก่อนใส่แรง
    """
    D = 1 - math.exp(-(K * pressure + A))
    return D


def ryshkewitch(porosity, max_tensile, b):
    """
    Ryshkewitch-Duckworth Equation: คำนวณ tensile strength
    
    Pharmacy logic:
    → วัดแรงยึดเกาะระหว่างอนุภาค
    → ยิ่ง porosity น้อย = tensile สูง = เม็ดยาแข็ง
    → เหมือนอิฐ: ยิ่งอัดแน่น ยิ่งแข็ง
    """
    tensile = max_tensile * math.exp(-b * porosity)
    return tensile


def fell_newton(tensile, diameter=8.0, thickness=4.0):
    """
    Fell-Newton Equation: แปลง tensile → hardness
    
    Pharmacy logic:
    → Hardness คือค่าที่วัดได้จริงในโรงงาน
    → เครื่อง hardness tester วัดค่านี้
    → USP กำหนด: 40-200 N ถือว่าผ่าน QC
    
    diameter  = เส้นผ่านศูนย์กลางเม็ดยา (mm)
    thickness = ความหนาเม็ดยา (mm)
    """
    hardness = tensile * math.pi * diameter * thickness / 2
    return hardness


# ============================================================
# MAIN SIMULATOR
# ============================================================

def simulate(excipient_name, pressure, diameter=8.0, thickness=4.0):
    """
    รับค่า excipient + pressure → คืนค่าทุกอย่าง
    
    นี่คือ pipeline หลักของโปรเจกต์:
    pressure → D → porosity → tensile → hardness → QC result
    """
    
    # ดึงค่า excipient จาก database
    if excipient_name not in EXCIPIENTS:
        print(f"ไม่พบ {excipient_name} ใน database")
        return None
    
    exc = EXCIPIENTS[excipient_name]
    
    # คำนวณตามลำดับ
    D        = heckel(pressure, exc["heckel_K"], exc["heckel_A"])
    porosity = 1 - D
    tensile  = ryshkewitch(porosity, exc["max_tensile"], exc["bonding_b"])
    hardness = fell_newton(tensile, diameter, thickness)
    
    # QC check ตาม USP
    if 40 <= hardness <= 200:
        qc = "✅ ผ่าน QC"
    elif hardness < 40:
        qc = "❌ เม็ดยาอ่อนเกินไป"
    else:
        qc = "❌ เม็ดยาแข็งเกินไป"
    
    # รวมผลลัพธ์
    result = {
        "excipient":  excipient_name,
        "pressure":   pressure,
        "density":    round(D, 4),
        "porosity":   round(porosity, 4),
        "tensile":    round(tensile, 4),
        "hardness":   round(hardness, 2),
        "qc":         qc
    }
    
    return result


def print_result(result):
    """แสดงผลลัพธ์แบบสวยงาม"""
    print("\n" + "="*45)
    print(f"  Tablet Compression Simulator v1.0")
    print("="*45)
    print(f"  Excipient : {result['excipient']}")
    print(f"  Pressure  : {result['pressure']} MPa")
    print("-"*45)
    print(f"  Density   : {result['density']}")
    print(f"  Porosity  : {result['porosity']}")
    print(f"  Tensile   : {result['tensile']} MPa")
    print(f"  Hardness  : {result['hardness']} N")
    print("-"*45)
    print(f"  QC Result : {result['qc']}")
    print("="*45)


# ============================================================
# OPTIMIZER
# ============================================================

def find_optimal_pressure(excipient_name,
                          target_min=40,
                          target_max=200,
                          start=50,
                          end=300,
                          step=10):
    """
    Pharmacy logic:
    → หา pressure ต่ำสุดที่ทำให้ hardness ผ่าน QC
    → ต่ำสุด = ดีสุด (ประหยัดพลังงาน + ลด wear ของ punch)

    คืนค่า dict:
      {"pressure": P, "hardness": H, "status": "...", "trace": [...]}
    ถ้าหาไม่เจอ pressure จะเป็น None และ status บอกสาเหตุ
    """
    print(f"\nกำลังหา optimal pressure สำหรับ {excipient_name}...")
    print("-" * 45)

    trace = []
    saw_too_soft = False
    saw_too_hard = False

    for P in range(start, end + 1, step):
        result = simulate(excipient_name, float(P))
        if result is None:
            return {"pressure": None, "hardness": None,
                    "status": "excipient not found", "trace": trace}

        hardness = result["hardness"]
        trace.append({"pressure": P, "hardness": hardness})

        if hardness < target_min:
            saw_too_soft = True
            print(f"P={P} MPa → Hardness={hardness:.1f} N ❌ อ่อนเกิน")
        elif hardness > target_max:
            saw_too_hard = True
            print(f"P={P} MPa → Hardness={hardness:.1f} N ❌ แข็งเกิน")
            if not saw_too_soft:
                print("  → ลองลดค่า start ให้ต่ำกว่านี้")
            break  # แข็งเกินแล้ว ไม่ต้องวิ่งต่อ
        else:
            print(f"P={P} MPa → Hardness={hardness:.1f} N ✅ ผ่าน QC")
            print(f"\n🎯 Optimal Pressure = {P} MPa")
            return {"pressure": P, "hardness": hardness,
                    "status": "ok", "trace": trace}

    if saw_too_hard and not saw_too_soft:
        status = "always too hard - ลดค่า start"
    elif saw_too_soft and not saw_too_hard:
        status = "always too soft - เพิ่มค่า end"
    else:
        status = "no passing pressure in range"

    print(f"ไม่พบ pressure ที่เหมาะสมในช่วงที่กำหนด ({status})")
    return {"pressure": None, "hardness": None, "status": status, "trace": trace}


# ============================================================
# MIXTURE (Rule of Mixtures / simple DoE)
# ============================================================

def mix_excipients(exc1_name, exc2_name, ratio_exc1):
    """
    ผสม excipient 2 ตัวตามสัดส่วน

    ratio_exc1 = สัดส่วนของตัวแรก (0.0 - 1.0)
    เช่น ratio_exc1 = 0.7 หมายถึง 70% exc1 + 30% exc2

    Pharmacy logic:
    → properties ของ mixture = weighted average
    → K_mix = K1 * ratio + K2 * (1-ratio)
    """
    if exc1_name not in EXCIPIENTS or exc2_name not in EXCIPIENTS:
        print("ไม่พบ excipient ที่ระบุ")
        return None

    if not 0.0 <= ratio_exc1 <= 1.0:
        print("ratio_exc1 ต้องอยู่ระหว่าง 0.0 - 1.0")
        return None

    exc1 = EXCIPIENTS[exc1_name]
    exc2 = EXCIPIENTS[exc2_name]
    ratio2 = 1 - ratio_exc1

    mixed = {
        "name": f"{exc1_name} {ratio_exc1*100:.0f}% + {exc2_name} {ratio2*100:.0f}%",
        "heckel_K":    exc1["heckel_K"]    * ratio_exc1 + exc2["heckel_K"]    * ratio2,
        "heckel_A":    exc1["heckel_A"]    * ratio_exc1 + exc2["heckel_A"]    * ratio2,
        "max_tensile": exc1["max_tensile"] * ratio_exc1 + exc2["max_tensile"] * ratio2,
        "bonding_b":   exc1["bonding_b"]   * ratio_exc1 + exc2["bonding_b"]   * ratio2,
        "density":     exc1["density"]     * ratio_exc1 + exc2["density"]     * ratio2,
    }
    return mixed


def simulate_mixture(exc1_name, exc2_name, ratio_exc1, pressure):
    """Simulate tablet จาก mixture ของ excipient 2 ตัว"""
    mixed = mix_excipients(exc1_name, exc2_name, ratio_exc1)
    if not mixed:
        return None

    D        = heckel(pressure, mixed["heckel_K"], mixed["heckel_A"])
    porosity = 1 - D
    tensile  = ryshkewitch(porosity, mixed["max_tensile"], mixed["bonding_b"])
    hardness = fell_newton(tensile)

    if 40 <= hardness <= 200:
        qc = "✅ ผ่าน QC"
    elif hardness < 40:
        qc = "❌ เม็ดยาอ่อนเกินไป"
    else:
        qc = "❌ เม็ดยาแข็งเกินไป"

    return {
        "excipient": mixed["name"],
        "pressure":  pressure,
        "density":   round(D, 4),
        "porosity":  round(porosity, 4),
        "tensile":   round(tensile, 4),
        "hardness":  round(hardness, 2),
        "qc":        qc,
    }


def scan_mixture_ratios(exc1_name, exc2_name, pressure):
    """
    สแกนทุกสัดส่วน 10%-90% ที่ pressure เดียวกัน หาสัดส่วนที่ผ่าน QC
    (DoE แบบง่าย - หา formulation space)
    """
    exc1_name = exc1_name.strip()
    exc2_name = exc2_name.strip()

    if exc1_name not in EXCIPIENTS or exc2_name not in EXCIPIENTS:
        print("ไม่พบ excipient ที่ระบุ")
        return []

    print(f"\nสแกน mixture: {exc1_name} + {exc2_name}")
    print(f"Pressure: {pressure} MPa")
    print("-" * 55)

    passed = []
    for ratio in range(10, 100, 10):
        r = ratio / 100
        result = simulate_mixture(exc1_name, exc2_name, r, pressure)
        if result:
            status = result["qc"]
            print(f"{exc1_name} {ratio}% + {exc2_name} {100-ratio}%"
                  f" → Hardness={result['hardness']:.1f} N {status}")
            if "✅" in status:
                passed.append((ratio, result["hardness"]))

    if passed:
        print("\n🎯 สัดส่วนที่ผ่าน QC:")
        for r, h in passed:
            print(f"   {exc1_name} {r}% → Hardness {h:.1f} N")
    else:
        print("\n❌ ไม่มีสัดส่วนที่ผ่าน QC ที่ pressure นี้")

    return passed


# ============================================================
# RUN
# ============================================================

def ask_pressure():
    """ถามค่าแรงกดจนกว่าจะได้ตัวเลขบวกที่ถูกต้อง"""
    while True:
        raw = input("กรอกแรงกด (MPa): ").strip().lstrip("﻿")
        try:
            value = float(raw)
        except ValueError:
            print("  กรุณากรอกเป็นตัวเลข เช่น 100")
            continue
        if value <= 0:
            print("  แรงกดต้องมากกว่า 0")
            continue
        return value


if __name__ == "__main__":

    print("เลือก mode:")
    print("1 = กรอก pressure เอง")
    print("2 = หา optimal pressure อัตโนมัติ")
    print("3 = สแกน mixture ratio")

    mode = input("เลือก (1/2/3): ").strip()

    if mode == "1":
        pressure = ask_pressure()
        for name in EXCIPIENTS:
            result = simulate(name, pressure)
            if result:
                print_result(result)

    elif mode == "2":
        for name in EXCIPIENTS:
            find_optimal_pressure(name)

    elif mode == "3":
        print("Excipient ที่มี:", list(EXCIPIENTS.keys()))
        exc1 = input("Excipient 1: ").strip()
        exc2 = input("Excipient 2: ").strip()
        pressure = ask_pressure()
        scan_mixture_ratios(exc1, exc2, pressure)

    else:
        print("ไม่รู้จัก mode นี้ (เลือก 1, 2 หรือ 3)")