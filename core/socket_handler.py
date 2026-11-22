# core/socket_handler.py
import socket
import json
import time
from config import HOSTS, PORTS, SOCKET_TIMEOUT, TOTAL_NODES
from utils.logger import log

def send_packet(node_id, to_node_id, packet):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(SOCKET_TIMEOUT)
        client.connect((HOSTS[to_node_id], PORTS[to_node_id]))
        client.sendall(json.dumps(packet).encode('utf-8'))
        client.close()
        return True
    except Exception:
        return False

def broadcast_status(sender_id, current_token_holder):
    """Gửi thông báo trạng thái cho tất cả các máy"""
    packet = {"type": "STATUS_UPDATE", "token_holder": current_token_holder}
    for i in range(TOTAL_NODES):
        if i != sender_id: # Không gửi cho chính mình
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(0.1) 
                client.connect((HOSTS[i], PORTS[i]))
                client.sendall(json.dumps(packet).encode('utf-8'))
                client.close()
                time.sleep(0.05) # Giãn cách thời gian gửi để tránh dồn ứ
            except: 
                pass

def start_server(node_id, callback):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORTS[node_id]))
    server.listen(5)
    log(node_id, f"Đang lắng nghe tại port {PORTS[node_id]}...", "SUCCESS")
    while True:
        try:
            conn, addr = server.accept()
            data = conn.recv(4096).decode('utf-8')
            conn.close()
            if data: 
                callback(json.loads(data))
        except: 
            pass