# applications/app_file.py
import os
import time
from utils.logger import log

def write_shared_file(node_id, data):
    """Ghi dữ liệu vào file dùng chung và file riêng của Node"""
    os.makedirs("shared_data", exist_ok=True)
    os.makedirs(os.path.join("shared_data", "node_data"), exist_ok=True)
    
    file_chung = os.path.join("shared_data", "shared_data.txt")
    file_rieng = os.path.join("shared_data", "node_data", f"node_{node_id}.txt")
    
    log(node_id, f"DANG GHI FILE: {data}", "WARNING")
    time.sleep(2) # Giả lập thời gian ghi
    
    dong_du_lieu = f"[Node {node_id}] {data}\n"
    
    with open(file_chung, "a", encoding="utf-8") as f:
        f.write(dong_du_lieu)
    with open(file_rieng, "a", encoding="utf-8") as f:
        f.write(dong_du_lieu)
        
    log(node_id, "Ghi file thành công!", "SUCCESS")