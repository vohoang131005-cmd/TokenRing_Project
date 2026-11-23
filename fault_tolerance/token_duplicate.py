# fault_tolerance/token_duplicate.py
from utils.logger import log

def resolve_token_conflict(node_id, current_token, incoming_token):
    """
    So sanh 2 Token. Giu lai Token co UUID nho hon.
    Tra ve (token_hop_le, bi_huy) — bi_huy=True neu Token hien tai bi huy.
    """
    current_uuid = current_token.get("uuid", "init")
    incoming_uuid = incoming_token.get("uuid", "init")

    if current_uuid == incoming_uuid:
        return current_token, False

    if current_uuid < incoming_uuid:
        log(node_id, f"Phat hien Token trung! Huy Token {incoming_uuid[:8]}... Giu lai {current_uuid[:8]}...", "WARNING")
        return current_token, True   # incoming bi huy
    else:
        log(node_id, f"Phat hien Token trung! Huy Token {current_uuid[:8]}... Giu lai {incoming_uuid[:8]}...", "WARNING")
        return incoming_token, False  # current bi huy