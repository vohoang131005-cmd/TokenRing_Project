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

from fault_tolerance.watchdog import Watchdog
from fault_tolerance.token_lost import TokenLostDetector
from fault_tolerance.token_duplicate import resolve_token_conflict
from fault_tolerance.bypass import handle_bypass
from fault_tolerance.membership import (
    send_join_request,
    handle_join_request,
    handle_leave_request
)

from distributed_properties.lamport_clock import LamportClock
from distributed_properties.vector_clock import VectorClock

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

        self.lamport = LamportClock()
        self.vector_clock = VectorClock(node_id, TOTAL_NODES)

        self.shared_dir = "shared_data"
        os.makedirs(self.shared_dir, exist_ok=True)

        self.clock_file = os.path.join(self.shared_dir, f"clock_node_{self.node_id}.json")

        self.watchdog = Watchdog(self.node_id, self)
        self.token_lost_detector = TokenLostDetector(self.node_id, self)
        self.ui = TerminalUI(self.node_id, self.handle_user_input)

        self.luu_clock()
        self.heartbeat_file = os.path.join(self.shared_dir, f"heartbeat_node_{self.node_id}.json")

    def luu_clock(self):
        try:
            du_lieu = {
                "node_id": self.node_id,
                "lamport_clock": self.lamport.time,
                "vector_clock": self.vector_clock.vector,
                "updated_at": time.time()
            }
            file_tam = self.clock_file + ".tmp"
            with open(file_tam, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f, ensure_ascii=False)
            os.replace(file_tam, self.clock_file)
        except Exception as e:
            logger.log(self.node_id, f"Loi luu Clock: {e}", "WARNING")

    def ghi_heartbeat(self):
        try:
            du_lieu = {"node_id": self.node_id, "timestamp": time.time()}
            file_tam = self.heartbeat_file + ".tmp"
            with open(file_tam, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f)
            os.replace(file_tam, self.heartbeat_file)
        except Exception:
            pass

    def dashboard_token_holder(self, holder_id):
        try:
            du_lieu = {
                "holder_id": holder_id,
                "updated_at": time.time(),
                "updated_by": self.node_id
            }
            file_tam = os.path.join(self.shared_dir, f"token_status_{self.node_id}.tmp")
            file_chinh = os.path.join(self.shared_dir, "token_status.json")

            with open(file_tam, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f, ensure_ascii=False)
            
            # Thêm đoạn này để tránh tranh chấp file trên Windows
            for _ in range(3):
                try:
                    os.replace(file_tam, file_chinh)
                    break
                except PermissionError:
                    time.sleep(0.1)
                    
        except Exception as e:
            # Bỏ qua lỗi này, không in ra log để đỡ rối
            pass

    def handle_user_input(self, msg):
        if self.is_frozen:
            return
        self.data_queue.put(msg)
        self.lamport.tick()
        self.vector_clock.tick()
        self.luu_clock()
        logger.log(self.node_id, f"Da them '{msg}' vao hang doi.", "SUCCESS")

    def start(self):
        threading.Thread(target=start_server, args=(self.node_id, self.process_packet), daemon=True).start()
        threading.Thread(target=self.watchdog.run, daemon=True).start()
        threading.Thread(target=self.token_lost_detector.run, daemon=True).start()
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()

        logger.log(self.node_id, f"Node da khoi dong.", "SUCCESS")

        if self.node_id != 0:
            send_join_request(self.node_id, TOTAL_NODES)

        if self.node_id == 0:
            threading.Timer(5.0, self.send_token).start()

        self.ui.run()

    def _heartbeat_loop(self):
        while True:
            self.ghi_heartbeat()
            time.sleep(5)

    def process_packet(self, packet):
        if self.is_frozen:
            return

        packet_type = packet.get("type")

        if packet_type == "JOIN":
            joining_node = packet["node_id"]
            self.lamport.tick()
            self.vector_clock.tick()
            self.luu_clock()
            self.next_node = handle_join_request(self.node_id, joining_node, TOTAL_NODES)
            return

        if packet_type == "JOIN_ACK":
            self.next_node = packet["next_node"]
            logger.log(self.node_id, f"Da cap nhat next_node = {self.next_node} sau JOIN_ACK.", "SUCCESS")
            return

        if packet_type == "LEAVE":
            leaving_node = packet["node_id"]
            self.next_node = handle_leave_request(self.node_id, leaving_node, TOTAL_NODES)
            logger.log(self.node_id, f"Da cap nhat next_node = {self.next_node} sau LEAVE.", "WARNING")
            return

        if packet_type == "STATUS_UPDATE":
            holder = packet["token_holder"]
            if self._last_holder == holder:
                return
            self._last_holder = holder

            if holder == self.node_id:
                self.ui.update_status(f"DANG GIU TOKEN (Lamport: {self.lamport.time})", True)
            else:
                self.ui.update_status(f"DANG DOI TOKEN (Token o Node {holder})", False)
            return

        if packet_type == "TOKEN":
            old_uuid = self.token.get("uuid", "init")
            self.token, incoming_discarded = resolve_token_conflict(self.node_id, self.token, packet)
            new_uuid = self.token.get("uuid", "init")

            # Neu Token hien tai bi huy (UUID thay doi) va node khong giu Token,
            # gui Token hop le di tiep de khong mat Token khoi vong
            if old_uuid != new_uuid and not self.is_holding_token:
                logger.log(self.node_id, "Token cu bi huy, gui Token hop le di tiep.", "WARNING")
                self.send_token()
                return

            if "lamport_time" in packet:
                self.lamport.update(packet["lamport_time"])
            if "vector_clock" in packet:
                self.vector_clock.update(packet["vector_clock"])
            else:
                self.vector_clock.tick()

            self.luu_clock()
            self.token_lost_detector.update_last_seen()
            self._last_holder = self.node_id

            self.dashboard_token_holder(self.node_id)
            broadcast_status(self.node_id, self.node_id)

            self.ui.update_tech_info(
                self.lamport.time,
                self.token.get("uuid", "init"),
                self.vector_clock.vector
            )
            self.ui.update_status("DANG GIU TOKEN (San sang ghi)", True)

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

                    elif data.strip().upper() == "LEAVE":
                        from fault_tolerance.membership import send_leave_request
                        logger.log(self.node_id, "DANG GUI YEU CAU LEAVE...", "WARNING")
                        send_leave_request(self.node_id, TOTAL_NODES)
                        self.ui.update_status("DA ROI MANG...", False)
                        self.is_frozen = True 
                        time.sleep(2)
                        os._exit(0)

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
                    logger.log(self.node_id, "DA RA KHOI VUNG GANG (Hoan tat)", "SUCCESS") # <-- THÊM DÒNG NÀY
                    self.release_token()
            else:
                self.send_token()

    def release_token(self):
        if self.is_holding_token:
            self.watchdog.stop_timer()
            self.is_holding_token = False
            self.token["status"] = "FREE"
            self.ui.update_status("DANG DOI TOKEN...", False)
            self.send_token()

    def send_token(self, bypass_count=0):
        if self.is_holding_token:
            return

        if bypass_count >= TOTAL_NODES - 1:
            logger.log(self.node_id, "TAT CA NODE DEU CHET! Dung gui Token.", "ERROR")
            return

        time.sleep(TOKEN_SPEED)

        self.token["lamport_time"] = self.lamport.tick()
        self.token["vector_clock"] = self.vector_clock.tick()
        self.luu_clock()
        self.token["holder_id"] = self.next_node

        max_retries = 3
        success = False

        for attempt in range(max_retries):
            success = send_packet(self.node_id, self.next_node, self.token)
            if success:
                break
            if attempt < max_retries - 1:
                time.sleep(1)

        if not success:
            self.next_node = handle_bypass(
                self.node_id,
                self.next_node,
                TOTAL_NODES,
                self.ui.update_status
            )
            self._last_holder = self.next_node
            broadcast_status(self.node_id, self.next_node)
            self.send_token(bypass_count + 1)


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