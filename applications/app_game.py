# applications/app_game.py
import random
import time
from utils.logger import log

def play_game(node_id, action):
    """Giả lập trò chơi tung xúc xắc"""
    log(node_id, f"DANG CHƠI GAME: {action}", "WARNING")
    time.sleep(2)
    ket_qua = random.randint(1, 6)
    log(node_id, f"Kết quả tung xúc xắc: {ket_qua}", "SUCCESS")
    return ket_qua