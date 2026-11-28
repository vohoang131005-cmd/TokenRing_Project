# main.py
import sys
import threading
import time
import queue
import os
import json

from config import TOTAL_NODES, TOKEN_SPEED
from core.socket_handler import send_packet, start_server, broadcast_status
from core.critical_section import access_critical_section

# Import các module Fault Tolerance
from fault_tolerance.watchdog import Watchdog
from fault_tolerance.token_lost import TokenLostDetector
from fault_tolerance.token_duplicate import resolve_token_conflict
from fault_tolerance.membership import send_join_request, handle_join_request

# Import các module Distributed Properties
from distributed_properties.lamport_clock import LamportClock
from distributed_properties.vector_clock import VectorClock

# Import các ứng dụng
from applications.app_vote import vote
from applications.app_print import print_document
from applications.app_file import write_shared_file
from applications.app_game import play_game
from applications.app_blockchain import add_block

import utils.logger as logger
from utils.ui import TerminalUI


class Node:
    def __init__(self, node_id):
        if node_id < 0 or node_id >= TOTAL_NODES:
            raise ValueError(f"Node ID phai nam trong khoang 0 den {TOTAL_NODES - 1}")

        self.node_id = node_id
        self.next_node = (node_id + 1) % TOTAL_NODES
        self.data_queue = queue.Queue()

        self.token = {
            "type": "TOKEN",
            "status": "FREE",
            "holder_id": node_id,
            "uuid": "init",
            "lamport_time": 0,
            "vector_clock": [0] * TOTAL_NODES
        }

        self.is_holding_token = False
        self.is_frozen = False
        self._last_holder = -1
        self._last_status_time = 0
        self._last_status_lamport = -1
        self._has_created_token = False
        self._joined_existing_ring = False
        self._send_lock = threading.RLock()
        self._status_lock = threading.Lock()

        self.lamport = LamportClock()
        self.vector_clock = VectorClock(node_id, TOTAL_NODES)
        
        self.shared_dir = "shared_data"
        os.makedirs(self.shared_dir, exist_ok=True)

        self.clock_file = os.path.join(self.shared_dir, f"clock_node_{self.node_id}.json")

        self.watchdog = Watchdog(self.node_id, self)
        self.token_lost_detector = TokenLostDetector(self.node_id, self)
        self.ui = TerminalUI(self.node_id, self.handle_user_input)

        self.luu_clock()

    def _safe_write_json(self, file_tam, file_chinh, du_lieu):
        with open(file_tam, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False)
        for attempt in range(5):
            try:
                os.replace(file_tam, file_chinh)
                return
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.05)

    def luu_clock(self):
        try:
            du_lieu = {
                "node_id": self.node_id,
                "lamport_clock": self.lamport.time,
                "vector_clock": self.vector_clock.vector,
                "updated_at": time.time()
            }
            file_tam = self.clock_file + ".tmp"
            self._safe_write_json(file_tam, self.clock_file, du_lieu)
        except Exception as e:
            logger.log(self.node_id, f"Loi luu Clock: {e}", "WARNING")

    def dashboard_token_holder(self, holder_id):
        try:
            du_lieu = {
                "holder_id": holder_id,
                "updated_at": time.time(),
                "updated_by": self.node_id
            }
            file_tam = os.path.join(self.shared_dir, f"token_status_{self.node_id}.tmp")
            file_chinh = os.path.join(self.shared_dir, "token_status.json")
            self._safe_write_json(file_tam, file_chinh, du_lieu)
        except Exception as e:
            logger.log(self.node_id, f"Loi cap nhat trang thai Token: {e}", "WARNING")

    def handle_user_input(self, msg):
        if self.is_frozen:
            return
        self.data_queue.put(msg)
        self.lamport.tick()
        self.vector_clock.tick()
        self.luu_clock()
        logger.log(self.node_id, f"Da them '{msg}' vao hang doi.", "SUCCESS")

    def start(self):
        threading.Thread(target=start_server, args=(self.node_id, self.process_packet, lambda: self.is_frozen), daemon=True).start()
        threading.Thread(target=self.watchdog.run, daemon=True).start()
        threading.Thread(target=self.token_lost_detector.run, daemon=True).start()

        logger.log(self.node_id, f"Node da khoi dong.", "SUCCESS")

        if self.node_id != 0:
            send_join_request(self.node_id, TOTAL_NODES)
        else:
            def _node0_join_or_init():
                if send_join_request(0, TOTAL_NODES):
                    self._joined_existing_ring = True

            threading.Thread(target=_node0_join_or_init, daemon=True).start()
            threading.Timer(5.0, self._send_initial_token).start()

        self.ui.run()

    def _send_initial_token(self):
        if not self._joined_existing_ring and not self.is_frozen:
            self.send_token()

    def process_packet(self, packet):
        if self.is_frozen:
            return

        packet_type = packet.get("type")

        if packet_type == "JOIN":
            joining_node = packet["node_id"]
            self.lamport.tick()
            self.vector_clock.tick()
            self.luu_clock()
            
            self.next_node = handle_join_request(self.node_id, joining_node)
            
            self._has_created_token = False
            self.token_lost_detector.reset()
            return

        if packet_type == "STATUS_UPDATE":
            holder = packet["token_holder"]
            timestamp = packet.get("timestamp", 0)
            lamport_time = packet.get("lamport_time", 0)

            with self._status_lock:
                if (lamport_time, timestamp) <= (self._last_status_lamport, self._last_status_time):
                    return
                if self._last_holder == holder:
                    self._last_status_lamport = lamport_time
                    self._last_status_time = timestamp
                    return

                self._last_status_lamport = lamport_time
                self._last_status_time = timestamp
                self._last_holder = holder

            if holder == self.node_id:
                self.ui.update_status(f"San sang ghi (Lamport: {self.lamport.time})", True)
            else:
                self.ui.update_status(f"DANG DOI TOKEN (Token o Node {holder})", False)
            return

        if packet_type == "TOKEN":
            # --- ĐO THỜI GIAN THỰC TẾ KHI TOKEN QUAY LẠI NODE 0 ---
            if self.node_id == 0:
                logger.log(self.node_id, f"BENCHMARK_END:{time.time()}", "INFO")
            
            resolved_token = resolve_token_conflict(self.node_id, self.token, packet)
            if resolved_token is None:
                return
            self.token = resolved_token

            if "lamport_time" in packet:
                self.lamport.update(packet["lamport_time"])
            if "vector_clock" in packet:
                self.vector_clock.update(packet["vector_clock"])
            else:
                self.vector_clock.tick()

            self.luu_clock()
            self.token_lost_detector.update_last_seen()
            with self._status_lock:
                self._last_holder = self.node_id
                self._last_status_lamport = self.lamport.time
                self._last_status_time = time.time()
            self._has_created_token = False
            
            self.dashboard_token_holder(self.node_id)
            broadcast_status(self.node_id, self.node_id, self.lamport.time)

            self.ui.update_tech_info(
                self.lamport.time,
                self.token.get("uuid", "init"),
                self.vector_clock.vector
            )
            self.ui.update_status("San sang ghi", True)

            if not self.data_queue.empty():
                self.is_holding_token = True
                self.token["status"] = "BUSY"
                self.watchdog.start_timer()
                self.ui.update_status("DANG GHI FILE VAO VUNG GANG...", True)

                while not self.data_queue.empty() and self.is_holding_token:
                    data = self.data_queue.get()

                    if data.strip().upper() == "TREO":
                        self.is_frozen = True
                        logger.log(self.node_id, "GIA LAP MAY BI TREO CUNG!", "ERROR")
                        self.ui.update_status("MAY DANG BI TREO CUNG...", False)
                        while True:
                            time.sleep(1)

                    elif data.strip().upper().startswith("VOTE"):
                        parts = data.strip().upper().split()
                        if len(parts) >= 2:
                            vote(self.node_id, parts[-1])
                        else:
                            logger.log(self.node_id, "Cu phap: VOTE A hoac VOTE B", "WARNING")
                            
                    elif data.strip().upper().startswith("PRINT"):
                        parts = data.strip().upper().split()
                        if len(parts) >= 2 and parts[1] == "VOTE":
                            print_document(self.node_id, "VOTE")
                        else:
                            print_document(self.node_id, "DATA")
                            
                    elif data.strip().upper().startswith("GAME"):
                        play_game(self.node_id, data)
                        
                    elif data.strip().upper().startswith("BLOCK"):
                        transaction = data.strip()[5:].strip()
                        if transaction:
                            add_block(self.node_id, transaction)
                        else:
                            logger.log(self.node_id, "Cu phap: BLOCK <noi dung>", "ERROR")

                    else:
                        write_shared_file(self.node_id, data)

                if self.is_holding_token:
                    self.release_token()
            else:
                self.send_token()

    def release_token(self):
        if self.is_frozen:
            self.watchdog.stop_timer()
            self.is_holding_token = False
            return
        if self.is_holding_token:
            self.watchdog.stop_timer()
            self.is_holding_token = False
            self.token["status"] = "FREE"
            self.ui.update_status("DANG DOI TOKEN...", False)
            self.send_token()

    def send_token(self):
        """Gửi Token cho máy kế tiếp (Có xử lý Bypass an toàn)"""
        with self._send_lock:
            if self.is_holding_token or self.is_frozen:
                return

            time.sleep(TOKEN_SPEED)

            # --- ĐO THỜI GIAN THỰC TẾ KHI TOKEN RỜI NODE 0 ---
            if self.node_id == 0:
                logger.log(self.node_id, f"BENCHMARK_START:{time.time()}", "INFO")

            # Thử gửi Token cho next_node hiện tại
            for attempt in range(3):
                self.token["lamport_time"] = self.lamport.tick()
                self.token["vector_clock"] = self.vector_clock.tick()
                self.token["holder_id"] = self.next_node
                self.luu_clock()

                if send_packet(self.node_id, self.next_node, self.token):
                    self._bypass_attempts = 0
                    self.ui.update_status(f"DANG DOI TOKEN (Token o Node {self.next_node})", False)
                    logger.log(self.node_id, f"Da gui Token toi Node {self.next_node}.", "INFO")
                    return  # Gửi thành công, thoát hàm

                logger.log(self.node_id, f"Gui Token that bai lan {attempt+1}", "WARNING")
                time.sleep(1)

            # Nếu thất bại 3 lần -> Bypass
            logger.log(self.node_id, f"Node {self.next_node} sap! Kich hoat Bypass...", "ERROR")
            
            # Tính toán node mới (bỏ qua node sập, tránh gửi cho chính mình)
            self.next_node = (self.next_node + 1) % TOTAL_NODES
            if self.next_node == self.node_id:
                self.next_node = (self.next_node + 1) % TOTAL_NODES

            self.ui.update_status(f"Bypass sang Node {self.next_node}...", False)

            # Thử gửi lại cho node mới
            time.sleep(TOKEN_SPEED)
            self.token["lamport_time"] = self.lamport.tick()
            self.token["vector_clock"] = self.vector_clock.tick()
            self.token["holder_id"] = self.next_node
            self.luu_clock()
            
            success_retry = send_packet(self.node_id, self.next_node, self.token)
            if success_retry:
                self._bypass_attempts = 0
                self.ui.update_status(f"DANG DOI TOKEN (Token o Node {self.next_node})", False)
                logger.log(self.node_id, f"Bypass thanh cong! Da gui Token toi Node {self.next_node}.", "SUCCESS")
            else:
                # Nếu vẫn thất bại, thử bypass tiếp (đệ quy có giới hạn)
                logger.log(self.node_id, f"Van khong gui duoc toi Node {self.next_node}. Thu bypass tiep...", "ERROR")
                
                if not hasattr(self, '_bypass_attempts'):
                    self._bypass_attempts = 0
                
                self._bypass_attempts += 1
                
                if self._bypass_attempts >= TOTAL_NODES:
                    logger.log(self.node_id, "Da thu tat ca cac Node, khong the gui Token!", "ERROR")
                    self._bypass_attempts = 0
                    return
                
                self.send_token()
                self._bypass_attempts = 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Cach dung: python main.py <node_id>")
        sys.exit(1)

    try:
        node_id = int(sys.argv[1])
        if node_id < 0 or node_id >= TOTAL_NODES:
            print(f"Node ID phai nam trong khoang 0 den {TOTAL_NODES - 1}")
            sys.exit(1)
    except ValueError:
        print("Node ID phai la so nguyen.")
        sys.exit(1)

    node = Node(node_id)
    node.start()