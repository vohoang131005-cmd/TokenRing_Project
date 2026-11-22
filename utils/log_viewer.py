
# utils/log_viewer.py
# Dashboard giam sat he thong Token Ring
# Tu dong thay doi kich thuoc khi thu nho/phong to Terminal.

import os
import sys
import json
import time
import ctypes
import shutil

from datetime import datetime


# ==================================================
# CAU HINH
# ==================================================

SO_NODE = 6
THOI_GIAN_CAP_NHAT = 0.5
SO_DONG_SU_KIEN = 10

CHIEU_RONG = 100
CHIEU_CAO = 30

KICH_THUOC_CU = None


# ==================================================
# DUONG DAN
# ==================================================

THU_MUC_GOC = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

THU_MUC_LOG = os.path.join(
    THU_MUC_GOC, "logs"
)

THU_MUC_SHARED = os.path.join(
    THU_MUC_GOC, "shared_data"
)

FILE_TOKEN = os.path.join(
    THU_MUC_SHARED, "token_status.json"
)


# ==================================================
# DU LIEU TOAN CUC
# ==================================================

SU_KIEN = []

SO_DONG_LOG_DA_DOC = {}

NOI_DUNG_CU = []

ANSI_HO_TRO = False


# ==================================================
# LAY KICH THUOC TERMINAL
# ==================================================

def lay_kich_thuoc_terminal():

    kich_thuoc = shutil.get_terminal_size(
        fallback=(100, 30)
    )

    rong = max(20, kich_thuoc.columns - 1)
    cao = max(10, kich_thuoc.lines)

    return rong, cao


# ==================================================
# BAT CHE DO ANSI TREN WINDOWS
# ==================================================

def bat_che_do_ansi():

    global ANSI_HO_TRO

    if os.name != "nt":
        ANSI_HO_TRO = True
        return

    try:

        kernel32 = ctypes.windll.kernel32

        stdout_handle = kernel32.GetStdHandle(-11)

        mode = ctypes.c_uint()

        if kernel32.GetConsoleMode(
            stdout_handle,
            ctypes.byref(mode)
        ):

            ANSI_HO_TRO = bool(
                kernel32.SetConsoleMode(
                    stdout_handle,
                    mode.value | 0x0004
                )
            )

    except Exception:

        ANSI_HO_TRO = False


# ==================================================
# TAO THU MUC
# ==================================================

def tao_thu_muc():

    os.makedirs(THU_MUC_LOG, exist_ok=True)

    os.makedirs(THU_MUC_SHARED, exist_ok=True)


# ==================================================
# DOC FILE JSON AN TOAN
# ==================================================

def doc_json(duong_dan):

    try:

        with open(
            duong_dan,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as tep:

            return json.load(tep)

    except (
        OSError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        TypeError
    ):

        return {}


# ==================================================
# DOC NODE DANG GIU TOKEN
# ==================================================

def doc_token_holder():

    data = doc_json(FILE_TOKEN)

    if not isinstance(data, dict):
        return None

    for ten in (
        "holder_id",
        "token_holder",
        "node_id",
        "current_holder"
    ):

        if ten in data:

            try:

                return int(data[ten])

            except (ValueError, TypeError):

                pass

    token = data.get("token")

    if isinstance(token, dict):

        for ten in (
            "holder_id",
            "node_id"
        ):

            if ten in token:

                try:

                    return int(token[ten])

                except (ValueError, TypeError):

                    pass

    return None


# ==================================================
# DOC LAMPORT VA VECTOR CLOCK
# ==================================================

def doc_clock(node_id):

    duong_dan = os.path.join(
        THU_MUC_SHARED,
        f"clock_node_{node_id}.json"
    )

    data = doc_json(duong_dan)

    if not isinstance(data, dict) or not data:

        return None, None

    lamport = None
    vector = None

    for ten in (
        "lamport_clock",
        "lamport_time",
        "lamport",
        "time"
    ):

        if ten in data:

            lamport = data[ten]
            break

    for ten in (
        "vector_clock",
        "vector"
    ):

        if ten in data:

            vector = data[ten]
            break

    if isinstance(vector, list):

        vector = "[" + ", ".join(
            str(x) for x in vector
        ) + "]"

    elif vector is not None:

        vector = str(vector)

    return lamport, vector


# ==================================================
# DOC LOG MOI
# ==================================================

def doc_log_moi():

    for node_id in range(SO_NODE):

        duong_dan = os.path.join(
            THU_MUC_LOG,
            f"node_{node_id}.log"
        )

        try:

            with open(
                duong_dan,
                "r",
                encoding="utf-8",
                errors="replace"
            ) as tep:

                cac_dong = tep.readlines()

        except OSError:

            continue

        da_doc = SO_DONG_LOG_DA_DOC.get(
            node_id,
            0
        )

        # Xu ly truong hop file log bi ghi lai
        if len(cac_dong) < da_doc:

            da_doc = 0

        dong_moi = cac_dong[da_doc:]

        SO_DONG_LOG_DA_DOC[node_id] = len(cac_dong)

        for dong in dong_moi:

            dong = dong.strip()

            if dong:

                SU_KIEN.append(dong)

        # Chi giu lai 200 su kien gan nhat
        if len(SU_KIEN) > 200:

            del SU_KIEN[:-200]


# ==================================================
# CAT CHUOI THEO CHIEU RONG
# ==================================================

def cat_chuoi(chuoi, do_dai):

    chuoi = str(chuoi)

    if do_dai <= 0:
        return ""

    if len(chuoi) > do_dai:

        if do_dai <= 3:
            return chuoi[:do_dai]

        return chuoi[:do_dai - 3] + "..."

    return chuoi


# ==================================================
# TAO DUONG KE
# ==================================================

def tao_duong_ke():

    return "+" + "-" * (CHIEU_RONG - 2) + "+"


# ==================================================
# TAO DONG BANG
# ==================================================

def dong_bang(noi_dung):

    rong = max(1, CHIEU_RONG - 4)

    noi_dung = cat_chuoi(
        noi_dung,
        rong
    )

    return "| " + noi_dung.ljust(rong) + " |"


# ==================================================
# TAO BANG CLOCK CO GIAN
# ==================================================

def tao_bang_clock():

    cac_dong = []

    # Tinh kich thuoc cot theo Terminal
    rong_node = 4

    rong_lamport = min(
        14,
        max(8, CHIEU_RONG // 5)
    )

    rong_vector = max(
        1,
        CHIEU_RONG - rong_node - rong_lamport - 10
    )

    # Tao duong ke
    duong_ke = (
        "+"
        + "-" * (rong_node + 2)
        + "+"
        + "-" * (rong_lamport + 2)
        + "+"
        + "-" * (rong_vector + 2)
        + "+"
    )

    cac_dong.append(duong_ke)

    # Tieu de cot
    dong_tieu_de = (
        "| "
        + "Node".ljust(rong_node)
        + " | "
        + cat_chuoi(
            "Lamport Clock",
            rong_lamport
        ).ljust(rong_lamport)
        + " | "
        + cat_chuoi(
            "Vector Clock",
            rong_vector
        ).ljust(rong_vector)
        + " |"
    )

    cac_dong.append(dong_tieu_de)

    cac_dong.append(duong_ke)

    # Du lieu tung Node
    for node_id in range(SO_NODE):

        lamport, vector = doc_clock(node_id)

        if lamport is None and vector is None:

            lamport_text = "CHUA CO DU LIEU"

            vector_text = "CHUA CO DU LIEU"

        else:

            lamport_text = (
                str(lamport)
                if lamport is not None
                else "-"
            )

            vector_text = (
                str(vector)
                if vector is not None
                else "-"
            )

        dong = (
            "| "
            + str(node_id).ljust(rong_node)
            + " | "
            + cat_chuoi(
                lamport_text,
                rong_lamport
            ).ljust(rong_lamport)
            + " | "
            + cat_chuoi(
                vector_text,
                rong_vector
            ).ljust(rong_vector)
            + " |"
        )

        cac_dong.append(dong)

    cac_dong.append(duong_ke)

    return cac_dong


# ==================================================
# TAO NOI DUNG DASHBOARD
# ==================================================

def tao_dashboard():

    doc_log_moi()

    token_holder = doc_token_holder()

    cac_dong = []

    # Tieu de
    cac_dong.append("=" * CHIEU_RONG)

    cac_dong.append(
        cat_chuoi(
            "DASHBOARD GIAM SAT HE THONG TOKEN RING",
            CHIEU_RONG
        ).center(CHIEU_RONG)
    )

    cac_dong.append(
        (
            "Thoi gian: "
            + datetime.now().strftime("%H:%M:%S")
        ).center(CHIEU_RONG)
    )

    cac_dong.append("=" * CHIEU_RONG)

    cac_dong.append("")

    # Trang thai Node
    cac_dong.append(
        "TRANG THAI CAC NODE".center(CHIEU_RONG)
    )

    cac_dong.append(tao_duong_ke())

    for node_id in range(SO_NODE):

        if token_holder == node_id:

            trang_thai = (
                f">>> Node {node_id}: DANG GIU TOKEN <<<"
            )

        elif token_holder is None:

            trang_thai = (
                f"Node {node_id}: CHUA CO DU LIEU TOKEN"
            )

        else:

            trang_thai = (
                f"Node {node_id}: DANG DOI TOKEN"
            )

        cac_dong.append(
            dong_bang(trang_thai)
        )

    cac_dong.append(tao_duong_ke())

    cac_dong.append("")

    # Thong tin Clock
    cac_dong.append(
        "THONG TIN CLOCK CUA CAC NODE".center(
            CHIEU_RONG
        )
    )

    cac_dong.extend(tao_bang_clock())

    cac_dong.append("")

    # Su kien Node
    cac_dong.append(
        "TAT CA SU KIEN NODE".center(CHIEU_RONG)
    )

    cac_dong.append(tao_duong_ke())

    # Tinh so dong LOG theo chieu cao Terminal
    so_dong_co_dinh = len(cac_dong) + 2

    so_dong_log = max(
        1,
        min(
            SO_DONG_SU_KIEN,
            CHIEU_CAO - so_dong_co_dinh
        )
    )

    if SU_KIEN:

        for su_kien in SU_KIEN[-so_dong_log:]:

            cac_dong.append(
                dong_bang(su_kien)
            )

    else:

        cac_dong.append(
            dong_bang("Chua co su kien moi")
        )

    cac_dong.append(tao_duong_ke())

    cac_dong.append(
        "Nhan Ctrl+C de thoat".center(
            CHIEU_RONG
        )
    )

    # Gioi han so dong theo chieu cao Terminal
    if len(cac_dong) > CHIEU_CAO - 1:

        cac_dong = cac_dong[:CHIEU_CAO - 1]

    return cac_dong


# ==================================================
# XOA MAN HINH VA VE TOAN BO
# ==================================================

def ve_toan_bo(cac_dong):

    sys.stdout.write("\033[2J")
    sys.stdout.write("\033[H")

    for vi_tri, dong in enumerate(
        cac_dong,
        start=1
    ):

        sys.stdout.write(
            f"\033[{vi_tri};1H"
        )

        sys.stdout.write("\033[2K")

        sys.stdout.write(dong)

    sys.stdout.flush()


# ==================================================
# CAP NHAT DONG THAY DOI
# ==================================================

def cap_nhat_dong(cac_dong_moi):

    global NOI_DUNG_CU

    so_dong_cu = len(NOI_DUNG_CU)

    so_dong_moi = len(cac_dong_moi)

    so_dong = max(
        so_dong_cu,
        so_dong_moi
    )

    for i in range(so_dong):

        if i < so_dong_cu:

            dong_cu = NOI_DUNG_CU[i]

        else:

            dong_cu = ""

        if i < so_dong_moi:

            dong_moi = cac_dong_moi[i]

        else:

            dong_moi = ""

        if dong_cu != dong_moi:

            sys.stdout.write(
                f"\033[{i + 1};1H"
            )

            sys.stdout.write("\033[2K")

            sys.stdout.write(dong_moi)

    sys.stdout.flush()

    NOI_DUNG_CU = cac_dong_moi[:]


# ==================================================
# HAM MAIN
# ==================================================

def main():

    global NOI_DUNG_CU
    global KICH_THUOC_CU
    global CHIEU_RONG
    global CHIEU_CAO

    tao_thu_muc()

    bat_che_do_ansi()

    if not ANSI_HO_TRO:

        print(
            "Khong bat duoc ANSI tren terminal nay."
        )

        print(
            "Hay chay bang Windows Terminal hoac PowerShell."
        )

        return

    try:

        # Lay kich thuoc ban dau
        KICH_THUOC_CU = lay_kich_thuoc_terminal()

        CHIEU_RONG = KICH_THUOC_CU[0]

        CHIEU_CAO = KICH_THUOC_CU[1]

        # Ve giao dien lan dau
        cac_dong = tao_dashboard()

        ve_toan_bo(cac_dong)

        NOI_DUNG_CU = cac_dong[:]

        # Vong lap cap nhat
        while True:

            time.sleep(THOI_GIAN_CAP_NHAT)

            # Kiem tra kich thuoc Terminal
            kich_thuoc_moi = lay_kich_thuoc_terminal()

            if kich_thuoc_moi != KICH_THUOC_CU:

                KICH_THUOC_CU = kich_thuoc_moi

                CHIEU_RONG = kich_thuoc_moi[0]

                CHIEU_CAO = kich_thuoc_moi[1]

                # Ve lai toan bo khi thay doi kich thuoc
                cac_dong_moi = tao_dashboard()

                ve_toan_bo(cac_dong_moi)

                NOI_DUNG_CU = cac_dong_moi[:]

            else:

                cac_dong_moi = tao_dashboard()

                if cac_dong_moi != NOI_DUNG_CU:

                    cap_nhat_dong(cac_dong_moi)

    except KeyboardInterrupt:

        # Hien lai con tro
        sys.stdout.write("\033[?25h")

        sys.stdout.write("\033[0m\n")

        sys.stdout.flush()

        print("Da dung Dashboard.")


# ==================================================
# CHAY CHUONG TRINH
# ==================================================

if __name__ == "__main__":

    main()
