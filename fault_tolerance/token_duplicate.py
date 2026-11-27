# fault_tolerance/token_duplicate.py
from utils.logger import log

def resolve_token_conflict(node_id, current_token, incoming_token):
    """
    So sánh 2 Token. Giữ lại Token có UUID nhỏ hơn.
    Trả về Token hợp lệ, hoặc None nếu Token đến là bản sao/trùng cần hủy.
    """
    current_uuid = current_token.get("uuid", "init")
    incoming_uuid = incoming_token.get("uuid", "init")
    
    if current_uuid != incoming_uuid:
        if current_uuid != "init" and (incoming_uuid == "init" or current_uuid < incoming_uuid):
            log(node_id, f"Phát hiện Token trùng! Hủy Token {incoming_uuid[:8]}... Giữ lại {current_uuid[:8]}...", "WARNING")
            return None
        else:
            log(node_id, f"Phát hiện Token trùng! Hủy Token {current_uuid[:8]}... Giữ lại {incoming_uuid[:8]}...", "WARNING")
            return incoming_token

    current_lamport = current_token.get("lamport_time", -1)
    incoming_lamport = incoming_token.get("lamport_time", 0)
    if current_uuid != "init" and incoming_lamport <= current_lamport:
        log(node_id, f"Phát hiện bản sao Token {incoming_uuid[:8]}... (Lamport {incoming_lamport} <= {current_lamport}). Đã hủy.", "WARNING")
        return None

    return incoming_token