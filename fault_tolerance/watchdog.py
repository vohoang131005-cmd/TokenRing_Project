# fault_tolerance/watchdog.py
import threading
import time
from config import TOKEN_HOLD_TIMEOUT
from utils.logger import log

class Watchdog:
    def __init__(self, node_id, node_instance):
        self.node_id = node_id
        self.node = node_instance
        self.start_time = None
        self.running = True

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        self.start_time = None

    def run(self):
        while self.running:
            if getattr(self.node, "is_frozen", False):
                time.sleep(1)
                continue
            if self.start_time is not None:
                elapsed = time.time() - self.start_time
                # Đếm ngược 30 giây
                if elapsed > TOKEN_HOLD_TIMEOUT:
                    log(self.node_id, f"WATCHDOG: Đã hết 30s giữ Token! Tự động nhả để nhường cho máy khác...", "ERROR")
                    self.force_release()
            time.sleep(1)

    def force_release(self):
        self.stop_timer()
        self.node.release_token()