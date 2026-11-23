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
            if self.start_time is not None:
                elapsed = time.time() - self.start_time
                if elapsed > TOKEN_HOLD_TIMEOUT:
                    log(self.node_id, f"WATCHDOG: Da het {TOKEN_HOLD_TIMEOUT}s giu Token! Tu dong nha...", "ERROR")
                    self.force_release()
            time.sleep(1)

    def force_release(self):
        self.stop_timer()
        # Khong giai phong neu node dang bi treo cung
        if getattr(self.node, 'is_frozen', False):
            log(self.node_id, "WATCHDOG: Node dang treo cung, khong the giai phong!", "ERROR")
            return
        self.node.release_token()