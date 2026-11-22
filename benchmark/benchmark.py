# benchmark/benchmark.py
import time
import os
import matplotlib.pyplot as plt
# from utils.logger import log
def run_benchmark():
    """Hàm giả lập đo lường hiệu năng"""
    os.makedirs("benchmark/charts", exist_ok=True)
    
    print("--- BẮT ĐẦU BENCHMARK ---")
    so_request = 100
    thoi_gian_cho = []
    
    # Giả lập thời gian xử lý trung bình của Token Ring (dựa trên sleep 2s)
    for i in range(1, so_request + 1):
        # Thời gian Token quay 1 vòng (giả lập) + thời gian ghi file (2s)
        latency = 2.0 + (i * 0.01) # Giả lập độ trễ tăng dần
        thoi_gian_cho.append(latency)
        
    total_time = sum(thoi_gian_cho)
    throughput = so_request / total_time # Số request/giây
    
    print(f"Tổng số request: {so_request}")
    print(f"Tổng thời gian: {total_time:.2f} giây")
    print(f"Throughput (Requests/giây): {throughput:.2f}")
    print(f"Latency trung bình: {total_time/so_request:.4f} giây")
    
    # Vẽ biểu đồ
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, so_request + 1), thoi_gian_cho, marker='o', linestyle='-', color='b')
    plt.title('Biểu đồ Latency (Thời gian chờ) của Token Ring')
    plt.xlabel('Số thứ tự Request')
    plt.ylabel('Thời gian chờ (giây)')
    plt.grid(True)
    
    chart_path = "benchmark/charts/latency_chart.png"
    plt.savefig(chart_path)
    plt.close()
    
    print(f"Đã lưu biểu đồ tại: {chart_path}")
    print("--- KẾT THÚC BENCHMARK ---")

if __name__ == "__main__":
    run_benchmark()