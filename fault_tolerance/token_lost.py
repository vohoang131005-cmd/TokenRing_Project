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
        self.lock = threading.Lock()

    def update_last_seen(self):
        """Cập nhật thời gian mỗi khi nhìn thấy Token"""
        with self.lock:
            self.last_seen_time = time.time()
            self.has_created_token = False

    def reset(self):
        """Reset lại bộ đếm thời gian khi Node JOIN lại"""
        with self.lock:
            self.last_seen_time = time.time()
            self.has_created_token = False

    def run(self):
        """Luồng chạy ngầm kiểm tra xem Token có bị mất không"""
        while self.running:
            time.sleep(1)

            # Nếu máy đang bị treo cứng thì im lặng
            if getattr(self.node, "is_frozen", False):
                continue

            with self.lock:
                elapsed = time.time() - self.last_seen_time

                # Chỉ tạo Token mới nếu:
                # 1. Quá 30s không thấy Token
                # 2. Chưa tạo Token mới trong chu kỳ này
                # 3. Không phải là máy đang giữ Token
                if elapsed > TOKEN_LOST_TIMEOUT and not self.has_created_token and not self.node.is_holding_token:
                    self.has_created_token = True
                    should_create = True
                else:
                    should_create = False

            if should_create:
                log(
                    self.node_id,
                    f"TOKEN LOST: Quá {TOKEN_LOST_TIMEOUT}s không thấy Token! Tạo Token mới...",
                    "ERROR"
                )
                self.create_new_token()

    def create_new_token(self):
        """Tạo Token mới với UUID mới để phục hồi hệ thống"""
        with self.lock:
            self.last_seen_time = time.time()

        new_uuid = str(uuid.uuid4())
        
        self.node.token = {
            "type": "TOKEN",
            "status": "FREE",
            "holder_id": self.node_id,
            "uuid": new_uuid,
            "lamport_time": self.node.lamport.time,
            "vector_clock": self.node.vector_clock.vector
        }

        log(
            self.node_id,
            f"Đã tạo Token mới (UUID: {new_uuid[:8]}...) và gửi đi.",
            "SUCCESS"
        )

        self.node.send_token()