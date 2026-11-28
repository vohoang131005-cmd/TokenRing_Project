# benchmark/mutex_proof.py
import os
import re
from datetime import datetime

# Đường dẫn tới thư mục log
THU_MUC_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
SO_NODE = 6

# Các từ khóa báo hiệu bắt đầu vào vùng găng (dựa trên log thực tế của bạn)
TU_KHOA_BAT_DAU = [
    "DANG GHI FILE",
    "DANG BO PHIEU",
    "DANG CHUAN BI TAI LIEU PDF",
    "DANG DAO BLOCK",
    "DANG CHOI GAME",
    "DANG TRUY CAP VUNG GANG"
]

# Các từ khóa báo hiệu kết thúc vùng găng
TU_KHOA_KET_THUC = [
    "Ghi file thanh cong",
    "Vote A thanh cong",
    "Vote B thanh cong",
    "DA IN PDF THANH CONG",
    "Da dao xong Block",
    "Ket qua tung xuc xac",
    "DA RA KHOI VUNG GANG",
    "Ghi du lieu vao file chung va file rieng thanh cong"
]

def phan_tich_log(node_id):
    """Đọc log của 1 node và trả về danh sách các khoảng thời gian vào vùng găng"""
    duong_dan = os.path.join(THU_MUC_LOG, f"node_{node_id}.log")
    if not os.path.exists(duong_dan):
        return []

    cac_khoang_thoi_gian = []
    thoi_gian_bat_dau = None

    with open(duong_dan, "r", encoding="utf-8", errors="replace") as f:
        for dong in f:
            # Tách thời gian (định dạng [HH:MM:SS])
            match = re.search(r'\[(\d{2}:\d{2}:\d{2})\]', dong)
            if not match:
                continue
            
            thoi_gian_str = match.group(1)
            # Chuyển đổi sang giây để dễ tính toán
            h, m, s = map(int, thoi_gian_str.split(':'))
            tong_giay = h * 3600 + m * 60 + s

            # Kiểm tra từ khóa bắt đầu
            if any(tu_khoa in dong for tu_khoa in TU_KHOA_BAT_DAU):
                thoi_gian_bat_dau = tong_giay
            
            # Kiểm tra từ khóa kết thúc
            if any(tu_khoa in dong for tu_khoa in TU_KHOA_KET_THUC):
                if thoi_gian_bat_dau is not None:
                    cac_khoang_thoi_gian.append((thoi_gian_bat_dau, tong_giay, dong.strip()))
                    thoi_gian_bat_dau = None

    return cac_khoang_thoi_gian

def chay_mutex_proof():
    print("============================================================")
    print("CHỨNG MINH TÍNH CHẤT MUTUAL EXCLUSION (LOẠI TRỪ TƯƠNG HỖ)")
    print("============================================================")
    
    tat_ca_khoang = []
    
    # Thu thập dữ liệu từ tất cả các Node
    for node_id in range(SO_NODE):
        khoang_thoi_gian = phan_tich_log(node_id)
        for start, end, raw_log in khoang_thoi_gian:
            tat_ca_khoang.append({
                "node": node_id,
                "start": start,
                "end": end,
                "log": raw_log
            })
    
    if not tat_ca_khoang:
        print("Không tìm thấy dữ liệu vùng găng nào trong file log.")
        print("Hãy chạy các Node và thực hiện vài lệnh (ghi file, vote,...) trước khi chạy script này.")
        return

    # Sắp xếp theo thời gian bắt đầu
    tat_ca_khoang.sort(key=lambda x: x["start"])
    
    print(f"Tìm thấy {len(tat_ca_khoang)} lần vào vùng găng từ log của {SO_NODE} Node.\n")
    
    vi_pham = False
    
    # Kiểm tra chéo xem có 2 node nào vào vùng găng cùng lúc không
    for i in range(len(tat_ca_khoang)):
        for j in range(i + 1, len(tat_ca_khoang)):
            a = tat_ca_khoang[i]
            b = tat_ca_khoang[j]
            
            # Nếu là cùng 1 node thì bỏ qua (vì 1 node tự xử lý tuần tự)
            if a["node"] == b["node"]:
                continue
                
            # Kiểm tra xem 2 khoảng thời gian có giao nhau không
            # Giao nhau nếu: start_a < end_b VÀ start_b < end_a
            if a["start"] < b["end"] and b["start"] < a["end"]:
                vi_pham = True
                print(f"[VI PHẠM] Phát hiện xung đột vùng găng!")
                print(f"  - Node {a['node']}: {a['log']}")
                print(f"  - Node {b['node']}: {b['log']}")
                print()
    
    if not vi_pham:
        print("=> KẾT LUẬN: KHÔNG CÓ XUNG ĐỘT XẢY RA.")
        print("=> Tất cả các Node đều vào vùng găng tuần tự. Tính chất Mutual Exclusion được BẢO TOÀN 100%.")
    else:
        print("=> KẾT LUẬN: PHÁT HIỆN XUNG ĐỘT. Tính chất Mutual Exclusion bị vi phạm!")

if __name__ == "__main__":
    chay_mutex_proof()