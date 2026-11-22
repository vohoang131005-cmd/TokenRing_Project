# fault_tolerance/token_duplicate.py
from utils.logger import log

def resolve_token_conflict(node_id, current_token, incoming_token):
    """
    So sánh 2 Token. Giữ lại Token có UUID nhỏ hơn.
    Trả về Token hợp lệ.
    """
    current_uuid = current_token.get("uuid", "init")
    incoming_uuid = incoming_token.get("uuid", "init")
    
    if current_uuid != incoming_uuid:
        if current_uuid < incoming_uuid:
            log(node_id, f"Phát hiện Token trùng! Hủy Token {incoming_uuid[:8]}... Giữ lại {current_uuid[:8]}...", "WARNING")
            return current_token
        else:
            log(node_id, f"Phát hiện Token trùng! Hủy Token {current_uuid[:8]}... Giữ lại {incoming_uuid[:8]}...", "WARNING")
            return incoming_token
    
    return current_token