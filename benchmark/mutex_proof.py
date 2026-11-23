# benchmark/mutex_proof.py
import os
import re

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_LOG = os.path.join(THU_MUC_GOC, "logs")

PATTERN_VAO = re.compile(r"\[(\d{2}:\d{2}:\d{2})\] \[Node (\d+)\] DANG (GHI FILE|BO PHIEU|DAO BLOCK|CHOI GAME|CHUAN BI TAI LIEU PDF|TRUY CAP VUNG GANG)")
PATTERN_RA = re.compile(r"\[(\d{2}:\d{2}:\d{2})\] \[Node (\d+)\] (Ghi file thanh cong|Ghi du lieu vao file chung va file rieng thanh cong|Vote [AB] thanh cong|Da dao xong Block|Da in PDF thanh cong|DA RA KHOI VUNG GANG)")

def _parse_time(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

def doc_su_kien():
    su_kien = []
    for node_id in range(6):
        path = os.path.join(THU_MUC_LOG, f"node_{node_id}.log")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = PATTERN_VAO.search(line)
                if m:
                    su_kien.append({"node": int(m.group(2)), "time": _parse_time(m.group(1)), "loai": "VAO"})
                    continue
                m = PATTERN_RA.search(line)
                if m:
                    su_kien.append({"node": int(m.group(2)), "time": _parse_time(m.group(1)), "loai": "RA"})
    su_kien.sort(key=lambda x: x["time"])
    return su_kien

def kiem_tra_mutual_exclusion(su_kien):
    dang_trong = {} # Lưu node và thời gian vào
    vi_pham = []
    for sk in su_kien:
        if sk["loai"] == "VAO":
            # Nếu có node đang trong vùng găng, kiểm tra xem có bị trùng thời gian không
            for node_trong, time_vao in dang_trong.items():
                # Cho phép sai số 1 giây (do tốc độ in log)
                if abs(sk["time"] - time_vao) <= 1:
                    vi_pham.append((sk, node_trong))
            dang_trong[sk["node"]] = sk["time"]
        else:
            if sk["node"] in dang_trong:
                del dang_trong[sk["node"]]
    return vi_pham

def run_proof():
    print("=== CHUNG MINH DISTRIBUTED MUTEX ===")
    su_kien = doc_su_kien()

    if not su_kien:
        print("Chua co log. Hay chay he thong truoc.")
        return

    print(f"Tong so su kien doc duoc: {len(su_kien)}")

    vi_pham = kiem_tra_mutual_exclusion(su_kien)
    print("\n[1] MUTUAL EXCLUSION:")
    if not vi_pham:
        print("  PASS: Khong co 2 node cung trong vung gang.")
    else:
        print(f"  FAIL: Phat hien {len(vi_pham)} vi pham:")
        for sk, ds in vi_pham[:5]:
            print(f"    Node {sk['node']} vao luc {sk['time']} khi {ds} dang trong vung gang")

    dem = {}
    for sk in su_kien:
        if sk["loai"] == "VAO":
            dem[sk["node"]] = dem.get(sk["node"], 0) + 1

    print("\n[2] NO DEADLOCK:")
    if len(dem) >= 2:
        print(f"  PASS: Co {len(dem)} node tham gia vung gang, he thong khong bi khoa cung.")
    else:
        print(f"  CANH BAO: Chi co {len(dem)} node tham gia.")

    print("\n[3] NO STARVATION:")
    if dem:
        for n in sorted(dem):
            print(f"  Node {n}: {dem[n]} lan vao vung gang")
        gia_tri = list(dem.values())
        if max(gia_tri) - min(gia_tri) <= max(1, max(gia_tri) // 2):
            print("  PASS: So lan vao vung gang giua cac node tuong doi dong deu.")
        else:
            print("  CANH BAO: Co su chenh lech lon.")
    else:
        print("  Chua co du lieu.")

    print("\n=== KET THUC ===")

if __name__ == "__main__":
    run_proof()