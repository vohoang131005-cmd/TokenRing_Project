# fault_tolerance/bypass.py
from utils.logger import log

def handle_bypass(node_id, current_next_node, total_nodes, ui_update_callback):
    """
    Xử lý khi phát hiện máy kế tiếp bị sập.
    Trả về ID của máy mới (đã nhảy cóc).
    """
    log(node_id, f"Node {current_next_node} sap! Kich hoat Bypass...", "ERROR")
    
    # Tính toán node mới (bỏ qua node sập)
    new_next_node = (current_next_node + 1) % total_nodes
    
    # Cập nhật giao diện
    if ui_update_callback:
        ui_update_callback(f"DANG DOI TOKEN (Token o Node {new_next_node})", False)
        
    log(node_id, f"Chuyen huong Token sang Node {new_next_node}", "WARNING")
    
    return new_next_node