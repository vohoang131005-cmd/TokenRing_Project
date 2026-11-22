# fault_tolerance/token_lost.py
import threading
import time
import uuid
from config import TOKEN_LOST_TIMEOUT
from utils.logger import log

class TokenLostDetector:
    def __init__(self, node_id, node_instance):
        self.node_id = node_id
        self.node = node_instance
        self.last_seen_time = time.time()
        self.running = True
        self.has_created_token = False

    def update_last_seen(self):
        self.last_seen_time = time.time()
        self.has_created_token = False

    def run(self):
        while self.running:
            time.sleep(1)
            
            # Nếu máy đang bị treo cứng thì im lặng
            if getattr(self.node, 'is_frozen', False):
                continue
                
            elapsed = time.time() - self.last_seen_time
            # Nếu quá 30s không thấy Token VÀ chưa tạo Token mới VÀ không phải là máy đang giữ Token
            if elapsed > TOKEN_LOST_TIMEOUT and not self.node.is_holding_token and not self.has_created_token:
                log(self.node_id, f"TOKEN LOST: Quá {TOKEN_LOST_TIMEOUT}s không thấy Token! Tạo Token mới...", "ERROR")
                self.create_new_token()
                self.has_created_token = True

    def create_new_token(self):
        self.last_seen_time = time.time()
        # Gắn UUID mới cho Token
        self.node.token = {"type": "TOKEN", "status": "FREE", "holder_id": self.node_id, "uuid": str(uuid.uuid4())}
        self.node.send_token()