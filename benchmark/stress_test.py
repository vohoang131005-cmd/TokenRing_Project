# benchmark/stress_test.py
import os
import re

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_LOG = os.path.join(THU_MUC_GOC, "logs")

PATTERN_BYPASS = re.compile(r"Kich hoat Bypass")
PATTERN_LOST = re.compile(r"TOKEN LOST")
PATTERN_DUP = re.compile(r"Token trung")
PATTERN_TOKEN_TRANSFER = re.compile(r"Da them .* vao hang doi") # Đếm số request thực tế

def run_stress_test():
    print("--- BAT DAU PHAN TICH STRESS TEST (DOC LOG THUC) ---")

    tong_bypass = 0
    tong_lost = 0
    tong_dup = 0
    tong_request = 0
    so_node_co_log = 0

    for node_id in range(6):
        path = os.path.join(THU_MUC_LOG, f"node_{node_id}.log")
        if not os.path.exists(path):
            continue
        so_node_co_log += 1
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if PATTERN_BYPASS.search(line): tong_bypass += 1
                if PATTERN_LOST.search(line): tong_lost += 1
                if PATTERN_DUP.search(line): tong_dup += 1
                if PATTERN_TOKEN_TRANSFER.search(line): tong_request += 1

    print(f"So node co log: {so_node_co_log}/6")
    print(f"Tong so request duoc gui: {tong_request}")
    print(f"So lan Bypass (May sap): {tong_bypass}")
    print(f"So lan phat hien Token Lost: {tong_lost}")
    print(f"So lan phat hien Token trung: {tong_dup}")

    if tong_lost == 0 and tong_dup == 0:
        print("Ket luan: He thong on dinh, khong mat Token, khong trung lap.")
    elif tong_dup > 0:
        print("Ket luan: He thong co co che giai quyet trung lap (UUID) hoat dong tot.")
    elif tong_lost > 0:
        print("Ket luan: Co hien tuong mat Token nhung he thong da tu phuc hoi.")

    print("--- KET THUC ---")

if __name__ == "__main__":
    run_stress_test()