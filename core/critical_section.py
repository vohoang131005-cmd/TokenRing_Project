
# core/critical_section.py
import os
import time
from utils.logger import log


def access_critical_section(node_id, data):
    """Ghi du lieu vao file chung va file rieng cua Node."""

    log(node_id, f"DANG TRUY CAP VUNG GANG: {data}", "WARNING")

    # Tao cac thu muc neu chua co
    os.makedirs("shared_data", exist_ok=True)
    os.makedirs(os.path.join("shared_data", "node_data"), exist_ok=True)

    # File du lieu chung
    file_chung = os.path.join("shared_data", "shared_data.txt")

    # File du lieu rieng cua Node
    file_rieng = os.path.join(
        "shared_data",
        "node_data",
        f"node_{node_id}.txt"
    )

    time.sleep(2)

    dong_du_lieu = f"[Node {node_id}] {data}\n"

    # Ghi vao file chung
    with open(file_chung, "a", encoding="utf-8") as f:
        f.write(dong_du_lieu)

    # Ghi vao file rieng
    with open(file_rieng, "a", encoding="utf-8") as f:
        f.write(dong_du_lieu)

    log(node_id, "Ghi du lieu vao file chung va file rieng thanh cong!", "SUCCESS")
