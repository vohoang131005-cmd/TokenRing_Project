# fault_tolerance/membership.py
import time
from core.socket_handler import send_packet
from utils.logger import log

def send_join_request(node_id, total_nodes):
    """Gui yeu cau JOIN toi may dung truoc."""
    time.sleep(2)
    join_packet = {"type": "JOIN", "node_id": node_id}
    prev_node = (node_id - 1) % total_nodes
    log(node_id, f"Gui yeu cau JOIN toi Node {prev_node}...", "INFO")
    send_packet(node_id, prev_node, join_packet)

def handle_join_request(node_id, joining_node, total_nodes):
    """
    Xu ly khi nhan yeu cau JOIN.
    Tra ve next_node moi cho node hien tai.
    Dong thoi gui JOIN_ACK cho node moi biet next_node cua no.
    """
    log(node_id, f"Nhan yeu cau JOIN tu Node {joining_node}. Cap nhat vong tron!", "SUCCESS")

    # Node moi se tro den node ke tiep cua node hien tai
    new_next_for_joiner = (node_id + 1) % total_nodes

    ack_packet = {
        "type": "JOIN_ACK",
        "next_node": new_next_for_joiner
    }
    send_packet(node_id, joining_node, ack_packet)

    return joining_node  # node hien tai tro den node moi

def send_leave_request(node_id, total_nodes):
    """Gui yeu cau LEAVE toi may dung truoc."""
    leave_packet = {"type": "LEAVE", "node_id": node_id}
    prev_node = (node_id - 1) % total_nodes
    log(node_id, f"Gui yeu cau LEAVE toi Node {prev_node}...", "INFO")
    send_packet(node_id, prev_node, leave_packet)

def handle_leave_request(node_id, leaving_node, total_nodes):
    """
    Xu ly khi nhan yeu cau LEAVE.
    Tra ve next_node moi (bo qua node roi).
    """
    log(node_id, f"Nhan yeu cau LEAVE tu Node {leaving_node}. Noi tat vong tron!", "WARNING")
    new_next = (leaving_node + 1) % total_nodes
    return new_next