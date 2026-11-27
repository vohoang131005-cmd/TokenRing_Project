# core/socket_handler.py
import socket
import json
import threading
import time
from config import HOSTS, PORTS, SOCKET_TIMEOUT, TOTAL_NODES
from utils.logger import log


def send_packet(node_id, to_node_id, packet):
    client = None
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(SOCKET_TIMEOUT)
        client.connect((HOSTS[to_node_id], PORTS[to_node_id]))
        data = json.dumps(packet).encode("utf-8")
        client.sendall(data)
        client.shutdown(socket.SHUT_WR)
        return True
    except Exception:
        return False
    finally:
        if client:
            client.close()


def broadcast_status(sender_id, current_token_holder, lamport_time=0):
    # Thêm timestamp và lamport_time vào gói tin để chống nhảy loạn
    packet = {
        "type": "STATUS_UPDATE",
        "token_holder": current_token_holder,
        "sender_id": sender_id,
        "lamport_time": lamport_time,
        "timestamp": time.time()
    }

    def _send(target_id):
        try:
            send_packet(sender_id, target_id, packet)
        except Exception:
            pass

    for i in range(TOTAL_NODES):
        if i == sender_id:
            continue
        threading.Thread(target=_send, args=(i,), daemon=True).start()


def handle_connection(conn, addr, callback, node_id):
    try:
        conn.settimeout(SOCKET_TIMEOUT)
        chunks = []
        while True:
            data = conn.recv(4096)
            if not data:
                break
            chunks.append(data)
        if chunks:
            packet_data = b"".join(chunks)
            packet = json.loads(packet_data.decode("utf-8"))
            threading.Thread(target=callback, args=(packet,), daemon=True).start()
    except Exception as e:
        log(node_id, f"Loi nhan goi tin tu {addr}: {e}", "ERROR")
    finally:
        conn.close()


def start_server(node_id, callback, is_frozen_fn=None):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORTS[node_id]))
    server.listen(50)
    server.settimeout(1.0)
    log(node_id, f"Dang lang nghe tai port {PORTS[node_id]}...", "SUCCESS")
    try:
        while True:
            if is_frozen_fn and is_frozen_fn():
                break
            try:
                conn, addr = server.accept()
                if is_frozen_fn and is_frozen_fn():
                    conn.close()
                    break
                threading.Thread(target=handle_connection, args=(conn, addr, callback, node_id), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                log(node_id, f"Loi server: {e}", "ERROR")
    finally:
        server.close()