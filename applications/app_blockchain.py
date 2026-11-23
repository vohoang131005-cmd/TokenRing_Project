# applications/app_blockchain.py
import json
import os
import hashlib
import time
from utils.logger import log


def calculate_hash(block_id, data, previous_hash, timestamp):
    raw_data = f"{block_id}{data}{previous_hash}{timestamp}"
    return hashlib.sha256(raw_data.encode()).hexdigest()


def validate_chain(chain):
    """Kiem tra tinh hop le cua toan bo chuoi."""
    if not chain:
        return True, "Chuoi rong"

    for i in range(1, len(chain)):
        block = chain[i]
        prev = chain[i - 1]
        if block.get("previous_hash") != prev.get("current_hash"):
            return False, f"Block {block.get('block_id')} co previous_hash khong khop"
    return True, "Chuoi hop le"


def add_block(node_id, transaction_data):
    file_path = os.path.join("shared_data", "blockchain.json")
    os.makedirs("shared_data", exist_ok=True)

    log(node_id, "DANG DAO BLOCK MOI...", "WARNING")
    time.sleep(2)

    chain = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                chain = json.load(f)
        except Exception:
            chain = []

    if len(chain) == 0:
        previous_hash = "0" * 64
        block_id = 1
    else:
        previous_hash = chain[-1]["current_hash"]
        block_id = len(chain) + 1

    timestamp = time.time()
    current_hash = calculate_hash(block_id, transaction_data, previous_hash, timestamp)

    new_block = {
        "block_id": block_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)),
        "data": transaction_data,
        "previous_hash": previous_hash,
        "current_hash": current_hash
    }

    chain.append(new_block)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chain, f, ensure_ascii=False, indent=4)

    hop_le, thong_bao = validate_chain(chain)
    if hop_le:
        log(node_id, f"Da dao xong Block {block_id}. Hash: {current_hash[:10]}... Chain hop le.", "SUCCESS")
    else:
        log(node_id, f"CANH BAO: {thong_bao}", "ERROR")