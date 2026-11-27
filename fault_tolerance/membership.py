# fault_tolerance/membership.py
import time
from core.socket_handler import send_packet
from utils.logger import log

def send_join_request(node_id, total_nodes):
    """Gửi yêu cầu JOIN tới máy sống gần nhất đứng trước."""
    time.sleep(2)  # Đợi server khởi động
    join_packet = {"type": "JOIN", "node_id": node_id}

    for offset in range(1, total_nodes):
        prev_node = (node_id - offset) % total_nodes
        log(node_id, f"Gui yeu cau JOIN toi Node {prev_node}...", "INFO")
        if send_packet(node_id, prev_node, join_packet):
            return True
        log(node_id, f"Node {prev_node} khong phan hoi JOIN, thu node truoc do...", "WARNING")

    log(node_id, "Khong tim thay node nao dang hoat dong de JOIN!", "ERROR")
    return False

def handle_join_request(node_id, joining_node):
    """Xử lý khi nhận được yêu cầu JOIN từ máy khác."""
    log(node_id, f"Nhan yeu cau JOIN tu Node {joining_node}. Cap nhat vong tron!", "SUCCESS")
    return joining_node # Trả về node mới để cập nhật next_node