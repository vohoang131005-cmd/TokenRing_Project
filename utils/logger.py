# utils/logger.py

from datetime import datetime
import os
import re
import threading
import unicodedata

LOGS = {}

KHOA_LOG = threading.Lock()

THU_MUC_GOC = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

THU_MUC_LOG = os.path.join(THU_MUC_GOC, "logs")


def strip_ansi(text):
    """Xoa ma mau ANSI."""
    return re.sub(r'\x1b\[[0-9;]*m', '', str(text))


def chuan_hoa_chuoi(text):
    """Chuyen chuoi ve chu thuong khong dau."""
    text = unicodedata.normalize("NFD", str(text))

    text = "".join(
        ky_tu for ky_tu in text
        if unicodedata.category(ky_tu) != "Mn"
    )

    return text.lower()


def log(node_id, message, level="INFO"):
    """
    Ghi log vao RAM va file.
    Khong hien thi thong bao gui Token thanh cong.
    """

    noi_dung = strip_ansi(message)

    # Loc thong bao gui Token thanh cong
    noi_dung_chuan = chuan_hoa_chuoi(noi_dung)

    if "da gui token toi node" in noi_dung_chuan:
        return

    thoi_gian = datetime.now().strftime("%H:%M:%S")

    dong_log = f"[{thoi_gian}] [Node {node_id}] {noi_dung}"

    with KHOA_LOG:

        # Luu log trong RAM cho giao dien Node
        if node_id not in LOGS:
            LOGS[node_id] = []

        LOGS[node_id].append(dong_log)

        if len(LOGS[node_id]) > 15:
            LOGS[node_id].pop(0)

        # Ghi log vao file cho Dashboard
        try:
            os.makedirs(THU_MUC_LOG, exist_ok=True)

            duong_dan = os.path.join(
                THU_MUC_LOG,
                f"node_{node_id}.log"
            )

            with open(
                duong_dan,
                "a",
                encoding="utf-8"
            ) as tep:

                tep.write(dong_log + "\n")

        except OSError:
            pass