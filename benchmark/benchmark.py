# benchmark/benchmark.py
import json
import os
import re
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_LOG = os.path.join(THU_MUC_GOC, "logs")
THU_MUC_CHART = os.path.join(THU_MUC_GOC, "benchmark", "charts")

# Mở rộng regex để bắt mọi loại lệnh
PATTERN_VAO = re.compile(r"\[(\d{2}:\d{2}:\d{2})\] \[Node (\d+)\] DANG (GHI FILE|BO PHIEU|DAO BLOCK|CHOI GAME|CHUAN BI TAI LIEU PDF|TRUY CAP VUNG GANG)")
PATTERN_RA = re.compile(r"\[(\d{2}:\d{2}:\d{2})\] \[Node (\d+)\] (Ghi file thanh cong|Ghi du lieu vao file chung va file rieng thanh cong|Vote [AB] thanh cong|Da dao xong Block|Da in PDF thanh cong|DA RA KHOI VUNG GANG)")

def _parse_time(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

def doc_log():
    ket_qua = []
    for node_id in range(6):
        path = os.path.join(THU_MUC_LOG, f"node_{node_id}.log")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        vao = None
        for line in lines:
            m_vao = PATTERN_VAO.search(line)
            if m_vao:
                vao = _parse_time(m_vao.group(1))
                continue
            m_ra = PATTERN_RA.search(line)
            if m_ra and vao is not None:
                ra = _parse_time(m_ra.group(1))
                if ra >= vao:
                    ket_qua.append({"node_id": node_id, "vao": vao, "ra": ra, "latency": ra - vao})
                vao = None
    return ket_qua

def run_benchmark():
    os.makedirs(THU_MUC_CHART, exist_ok=True)
    print("--- BAT DAU BENCHMARK (DOC LOG THUC) ---")
    du_lieu = doc_log()

    if not du_lieu:
        print("Chua co du lieu log. Hay chay 6 node va gui yeu cau truoc.")
        return

    latencies = [d["latency"] for d in du_lieu]
    so_request = len(du_lieu)
    total_time = sum(latencies)
    throughput = so_request / total_time if total_time > 0 else 0

    print(f"Tong so request do duoc: {so_request}")
    print(f"Tong latency: {total_time} giay")
    print(f"Throughput: {throughput:.4f} req/giay")
    print(f"Latency trung binh: {total_time / so_request:.4f} giay")
    print(f"Latency min/max: {min(latencies)}/{max(latencies)} giay")

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, so_request + 1), latencies, marker="o", linestyle="-", color="b")
    plt.title("Latency thuc te cua Token Ring (doc tu log)")
    plt.xlabel("So thu tu Request")
    plt.ylabel("Latency (giay)")
    plt.grid(True)
    chart1 = os.path.join(THU_MUC_CHART, "latency_real.png")
    plt.savefig(chart1)
    plt.close()

    dem_node = {}
    for d in du_lieu:
        dem_node[d["node_id"]] = dem_node.get(d["node_id"], 0) + 1

    plt.figure(figsize=(8, 5))
    nodes = sorted(dem_node.keys())
    counts = [dem_node[n] for n in nodes]
    plt.bar([f"Node {n}" for n in nodes], counts, color="g")
    plt.title("So request thuc hien boi tung Node")
    plt.xlabel("Node")
    plt.ylabel("So request")
    chart2 = os.path.join(THU_MUC_CHART, "requests_per_node.png")
    plt.savefig(chart2)
    plt.close()

    ket_qua = {
        "so_request": so_request,
        "throughput": throughput,
        "latency_trung_binh": total_time / so_request,
        "latency_min": min(latencies),
        "latency_max": max(latencies),
        "do_lech_node": dem_node,
        "thoi_gian_do": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    json_path = os.path.join(THU_MUC_CHART, "benchmark_result.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ket_qua, f, ensure_ascii=False, indent=4)

    print(f"Da luu bieu do: {chart1}, {chart2}")
    print(f"Da luu ket qua: {json_path}")
    print("--- KET THUC BENCHMARK ---")

if __name__ == "__main__":
    run_benchmark()