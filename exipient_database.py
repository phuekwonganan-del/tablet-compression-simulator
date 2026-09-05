"""
Pharmaceutical Tablet Compression Simulator
Excipient Database v1.0
Author: Tok
"""

from mainproject_physicc_engine import EXCIPIENTS

# ============================================================
# EXTENDED EXCIPIENT DATABASE
# ============================================================
# เพิ่ม properties ที่ machine module ต้องการ
# flow, compressibility, moisture sensitivity

EXCIPIENT_EXTENDED = {

    "MCC_PH102": {
        # Physics (มีแล้วใน physics_engine)
        "heckel_K":    0.0128,
        "heckel_A":    0.42,
        "max_tensile": 9.5,
        "bonding_b":   6.5,
        "density":     1.512,
        
        # Flow Properties
        "carr_index":      18.5,   # % (< 25 = acceptable)
        "hausner_ratio":   1.23,   # (< 1.25 = acceptable)
        "angle_of_repose": 38.0,   # degrees (< 40 = good flow)
        "flow_grade":      "Good",
        
        # Compressibility
        "compressibility": "Excellent",
        "lubricant_needed": True,
        
        # Sensitivity
        "moisture_sensitive": False,
        "hygroscopic":        False,
        
        # Usage
        "common_use":  "Filler, Binder, Disintegrant",
        "max_percent": 80,         # % in formulation
        "cost_grade":  "Medium",
    },

    "Lactose_DC": {
        "heckel_K":    0.0082,
        "heckel_A":    0.35,
        "max_tensile": 5.2,
        "bonding_b":   5.8,
        "density":     1.545,
        
        "carr_index":      22.0,
        "hausner_ratio":   1.28,
        "angle_of_repose": 42.0,
        "flow_grade":      "Fair",
        
        "compressibility": "Good",
        "lubricant_needed": True,
        
        "moisture_sensitive": True,
        "hygroscopic":        True,
        
        "common_use":  "Filler, Diluent",
        "max_percent": 80,
        "cost_grade":  "Low",
    },

    "DCP": {
        "heckel_K":    0.0045,
        "heckel_A":    0.28,
        "max_tensile": 3.8,
        "bonding_b":   4.2,
        "density":     2.890,
        
        "carr_index":      15.0,
        "hausner_ratio":   1.18,
        "angle_of_repose": 35.0,
        "flow_grade":      "Excellent",
        
        "compressibility": "Poor",
        "lubricant_needed": True,
        
        "moisture_sensitive": False,
        "hygroscopic":        False,
        
        "common_use":  "Filler, Diluent",
        "max_percent": 85,
        "cost_grade":  "Low",
    },

    "Starch_1500": {
        "heckel_K":    0.0095,
        "heckel_A":    0.38,
        "max_tensile": 4.1,
        "bonding_b":   5.2,
        "density":     1.478,
        
        "carr_index":      28.0,
        "hausner_ratio":   1.39,
        "angle_of_repose": 45.0,
        "flow_grade":      "Poor",
        
        "compressibility": "Fair",
        "lubricant_needed": True,
        
        "moisture_sensitive": True,
        "hygroscopic":        True,
        
        "common_use":  "Disintegrant, Binder",
        "max_percent": 20,
        "cost_grade":  "Low",
    },

    "Mannitol_DC": {
        "heckel_K":    0.0075,
        "heckel_A":    0.32,
        "max_tensile": 4.8,
        "bonding_b":   5.5,
        "density":     1.514,
        
        "carr_index":      16.0,
        "hausner_ratio":   1.19,
        "angle_of_repose": 36.0,
        "flow_grade":      "Good",
        
        "compressibility": "Good",
        "lubricant_needed": True,
        
        "moisture_sensitive": False,
        "hygroscopic":        False,
        
        "common_use":  "Filler, Sweetener (chewable tablet)",
        "max_percent": 90,
        "cost_grade":  "High",
    },
}

# ============================================================
# FUNCTIONS
# ============================================================

def get_excipient_info(name):
    """ดูข้อมูล excipient แบบละเอียด"""
    
    if name not in EXCIPIENT_EXTENDED:
        print(f"ไม่พบ {name}")
        return None
    
    return EXCIPIENT_EXTENDED[name]


def print_excipient_profile(name):
    """แสดง profile ของ excipient แบบสวยงาม"""
    
    exc = get_excipient_info(name)
    if not exc:
        return
    
    print(f"\n{'='*50}")
    print(f"  Excipient Profile: {name}")
    print(f"{'='*50}")
    print(f"  Common Use    : {exc['common_use']}")
    print(f"  Max % in form : {exc['max_percent']} %")
    print(f"  Cost          : {exc['cost_grade']}")
    print(f"{'-'*50}")
    print(f"  Flow Grade    : {exc['flow_grade']}")
    print(f"  Carr Index    : {exc['carr_index']} %")
    print(f"  Hausner Ratio : {exc['hausner_ratio']}")
    print(f"  Angle of Repose: {exc['angle_of_repose']}°")
    print(f"{'-'*50}")
    print(f"  Compressibility: {exc['compressibility']}")
    print(f"  Moisture Sensitive: {exc['moisture_sensitive']}")
    print(f"  Hygroscopic   : {exc['hygroscopic']}")
    print(f"{'='*50}")


def recommend_excipient(need_flow=True, 
                        need_compression=True,
                        moisture_ok=False):
    """
    แนะนำ excipient ตาม requirement
    
    Pharmacy logic:
    → ถ้า powder flow ไม่ดี → เครื่องตันได้
    → ถ้า compressibility ไม่ดี → ยาไม่แข็งพอ
    → ถ้า moisture sensitive → ต้องระวัง storage
    """
    
    flow_good    = ["Excellent", "Good"]
    compress_good = ["Excellent", "Good"]
    
    print(f"\n{'='*50}")
    print(f"  Excipient Recommendation")
    print(f"{'='*50}")
    
    recommended = []
    
    for name, exc in EXCIPIENT_EXTENDED.items():
        
        flow_pass    = exc["flow_grade"] in flow_good if need_flow else True
        compress_pass = exc["compressibility"] in compress_good if need_compression else True
        moisture_pass = not exc["moisture_sensitive"] if not moisture_ok else True
        
        if flow_pass and compress_pass and moisture_pass:
            recommended.append(name)
            print(f"  ✅ {name}")
            print(f"     Flow: {exc['flow_grade']}")
            print(f"     Compressibility: {exc['compressibility']}")
            print(f"     Cost: {exc['cost_grade']}")
            print()
    
    if not recommended:
        print("  ไม่พบ excipient ที่ตรงทุก requirement")
    
    return recommended


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    
    print("="*50)
    print("  Excipient Database v1.0")
    print("="*50)
    print("1 = ดู excipient profile")
    print("2 = แนะนำ excipient")
    print("3 = ดูทั้งหมด")
    
    mode = input("เลือก (1/2/3): ")
    
    if mode == "1":
        print("Excipient ที่มี:", list(EXCIPIENT_EXTENDED.keys()))
        name = input("Excipient: ").strip()
        print_excipient_profile(name)
    
    elif mode == "2":
        print("\nกำหนด requirement:")
        need_flow    = input("ต้องการ flow ดี? (y/n): ").lower() == "y"
        need_comp    = input("ต้องการ compressibility ดี? (y/n): ").lower() == "y"
        moisture_ok  = input("ยอมรับ moisture sensitive? (y/n): ").lower() == "y"
        recommend_excipient(need_flow, need_comp, moisture_ok)
    
    elif mode == "3":
        for name in EXCIPIENT_EXTENDED:
            print_excipient_profile(name)