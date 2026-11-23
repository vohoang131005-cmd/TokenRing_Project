# Thêm hàm này vào phần DOC DU LIEU (sau doc_clock)
def doc_heartbeat(node_id):
    duong_dan = os.path.join(
        THU_MUC_SHARED, f"heartbeat_node_{node_id}.json"
    )
    data = doc_json(duong_dan)
    if not isinstance(data, dict) or "timestamp" not in data:
        return None
    return time.time() - data["timestamp"]  # so giay tu lan cuoi


# Thay the ham tao_dashboard() bang phien ban nay
def tao_dashboard():
    doc_log_moi()
    token_holder = doc_token_holder()
    cac_dong = []

    cac_dong.append("=" * CHIEU_RONG)
    cac_dong.append(
        cat_chuoi(
            "DASHBOARD GIAM SAT HE THONG TOKEN RING",
            CHIEU_RONG
        ).center(CHIEU_RONG)
    )
    cac_dong.append(
        ("Thoi gian: " + datetime.now().strftime("%H:%M:%S")).center(CHIEU_RONG)
    )
    cac_dong.append("=" * CHIEU_RONG)
    cac_dong.append("")

    cac_dong.append("TRANG THAI CAC NODE".center(CHIEU_RONG))
    cac_dong.append(tao_duong_ke())

    for node_id in range(SO_NODE):
        hb = doc_heartbeat(node_id)
        if hb is None:
            song = "CHUA CO HEARTBEAT"
        elif hb > 15:
            song = f"MAT KET NOI ({int(hb)}s)"
        else:
            song = f"SONG ({int(hb)}s)"

        if token_holder == node_id:
            trang_thai = f">>> Node {node_id}: DANG GIU TOKEN <<< [{song}]"
        elif token_holder is None:
            trang_thai = f"Node {node_id}: CHUA CO DU LIEU TOKEN [{song}]"
        else:
            trang_thai = f"Node {node_id}: DANG DOI TOKEN [{song}]"

        cac_dong.append(dong_bang(trang_thai))

    cac_dong.append(tao_duong_ke())
    cac_dong.append("")
    cac_dong.append("THONG TIN CLOCK CUA CAC NODE".center(CHIEU_RONG))
    cac_dong.extend(tao_bang_clock())
    cac_dong.append("")
    cac_dong.append("TAT CA SU KIEN NODE".center(CHIEU_RONG))
    cac_dong.append(tao_duong_ke())

    so_dong_co_dinh = len(cac_dong) + 2
    so_dong_log = max(1, min(SO_DONG_SU_KIEN, CHIEU_CAO - so_dong_co_dinh))

    if SU_KIEN:
        for su_kien in SU_KIEN[-so_dong_log:]:
            cac_dong.append(dong_bang(su_kien))
    else:
        cac_dong.append(dong_bang("Chua co su kien moi"))

    cac_dong.append(tao_duong_ke())
    cac_dong.append("Nhan Ctrl+C de thoat".center(CHIEU_RONG))

    if len(cac_dong) > CHIEU_CAO - 1:
        cac_dong = cac_dong[:CHIEU_CAO - 1]

    return cac_dong