# applications/app_game.py
import json
import os
import random
import time
from datetime import datetime
from utils.logger import log


def _doc_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _ghi_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    os.replace(tmp, path)


def play_game(node_id, action):
    """Game nhieu nguoi: tung xuc xac, luu ket qua chung + lich su rieng."""
    log(node_id, f"DANG CHOI GAME: {action}", "WARNING")
    time.sleep(2)

    ket_qua = random.randint(1, 6)

    file_chung = os.path.join("shared_data", "game_results.json")
    file_rieng = os.path.join(
        "shared_data", "game_history", f"node_{node_id}.json"
    )

    # Doc ket qua chung
    du_lieu_chung = _doc_json(file_chung, {
        "tong_lan_tung": 0,
        "lich_su": [],
        "diem_cao_nhat": 0
    })
    du_lieu_chung.setdefault("tong_lan_tung", 0)
    du_lieu_chung.setdefault("lich_su", [])
    du_lieu_chung.setdefault("diem_cao_nhat", 0)

    thoi_gian = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    du_lieu_chung["tong_lan_tung"] += 1
    du_lieu_chung["lich_su"].append({
        "node_id": node_id,
        "ket_qua": ket_qua,
        "thoi_gian": thoi_gian
    })
    if ket_qua > du_lieu_chung["diem_cao_nhat"]:
        du_lieu_chung["diem_cao_nhat"] = ket_qua

    _ghi_json(file_chung, du_lieu_chung)

    # Doc lich su rieng
    lich_su_rieng = _doc_json(file_rieng, [])
    if not isinstance(lich_su_rieng, list):
        lich_su_rieng = []
    lich_su_rieng.append({"ket_qua": ket_qua, "thoi_gian": thoi_gian})
    _ghi_json(file_rieng, lich_su_rieng)

    log(
        node_id,
        f"Ket qua tung xuc xac: {ket_qua}. "
        f"Tong so lan tung toan he thong: {du_lieu_chung['tong_lan_tung']}. "
        f"Diem cao nhat: {du_lieu_chung['diem_cao_nhat']}",
        "SUCCESS"
    )
    return ket_qua