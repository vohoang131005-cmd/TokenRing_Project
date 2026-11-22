# applications/app_blockchain.py
import json
import os
import hashlib
import time
from utils.logger import log

def calculate_hash(block_id, data, previous_hash, timestamp):
    """Tính mã Hash SHA-256 cho block"""
    raw_data = f"{block_id}{data}{previous_hash}{timestamp}"
    return hashlib.sha256(raw_data.encode()).hexdigest()

def add_block(node_id, transaction_data):
    """Thêm một block mới vào chuỗi Blockchain"""
    file_path = os.path.join("shared_data", "blockchain.json")
    os.makedirs("shared_data", exist_ok=True)
    
    log(node_id, f"ĐANG ĐÀO BLOCK MỚI...", "WARNING")
    time.sleep(2) # Giả lập thời gian xử lý (Proof of Work)
    
    # 1. Đọc chuỗi hiện tại
    chain = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                chain = json.load(f)
        except:
            chain = []
            
    # 2. Lấy thông tin block trước đó
    if len(chain) == 0:
        previous_hash = "0" * 64 # Mã hash khởi tạo (Genesis Block)
        block_id = 1
    else:
        previous_hash = chain[-1]["current_hash"]
        block_id = len(chain) + 1
        
    # 3. Tạo block mới
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
    
    # 4. Ghi lại toàn bộ chuỗi vào file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chain, f, ensure_ascii=False, indent=4)
        
    log(node_id, f"Đã đào xong Block {block_id}. Hash: {current_hash[:10]}...", "SUCCESS")