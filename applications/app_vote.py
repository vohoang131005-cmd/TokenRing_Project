
# applications/app_vote.py
import json
import os
import time
from datetime import datetime
from utils.logger import log


def vote(node_id, candidate):
    candidate = candidate.strip().upper()

    # Chi chap nhan A hoac B
    if candidate not in ["A", "B"]:
        log(node_id, f"Ung vien {candidate} khong hop le!", "ERROR")
        return False

    os.makedirs("shared_data", exist_ok=True)
    os.makedirs(
        os.path.join("shared_data", "vote_history"),
        exist_ok=True
    )

    # File tong hop so phieu
    file_tong = os.path.join("shared_data", "votes.json")

    # File lich su vote rieng cua Node
    file_rieng = os.path.join(
        "shared_data",
        "vote_history",
        f"node_{node_id}.json"
    )

    log(node_id, f"DANG BO PHIEU CHO: {candidate}", "WARNING")
    time.sleep(2)

    # Doc tong so phieu
    du_lieu_tong = {"A": 0, "B": 0}

    if os.path.exists(file_tong):
        try:
            with open(file_tong, "r", encoding="utf-8") as f:
                du_lieu_tong = json.load(f)

            du_lieu_tong.setdefault("A", 0)
            du_lieu_tong.setdefault("B", 0)

        except (json.JSONDecodeError, OSError):
            du_lieu_tong = {"A": 0, "B": 0}

    # Cong them phieu
    du_lieu_tong[candidate] += 1

    file_tong_tam = file_tong + ".tmp"
    with open(file_tong_tam, "w", encoding="utf-8") as f:
        json.dump(
            du_lieu_tong,
            f,
            ensure_ascii=False,
            indent=4
        )
    os.replace(file_tong_tam, file_tong)

    # Doc lich su vote cua Node
    lich_su = []

    if os.path.exists(file_rieng):
        try:
            with open(file_rieng, "r", encoding="utf-8") as f:
                lich_su = json.load(f)

            if not isinstance(lich_su, list):
                lich_su = []

        except (json.JSONDecodeError, OSError):
            lich_su = []

    # Them lan vote moi
    lan_vote = {
        "node_id": node_id,
        "candidate": candidate,
        "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    lich_su.append(lan_vote)

    file_rieng_tam = file_rieng + ".tmp"
    with open(file_rieng_tam, "w", encoding="utf-8") as f:
        json.dump(
            lich_su,
            f,
            ensure_ascii=False,
            indent=4
        )
    os.replace(file_rieng_tam, file_rieng)

    log(
        node_id,
        f"Vote {candidate} thanh cong. Tong phieu {candidate}: {du_lieu_tong[candidate]}",
        "SUCCESS"
    )

    return True
