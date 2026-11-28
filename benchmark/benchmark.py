# benchmark/benchmark.py
import os
import re
import matplotlib.pyplot as plt

def run_benchmark():
    """Đọc log thực tế từ Node 0 và vẽ biểu đồ Latency"""
    log_file = os.path.join("logs", "node_0.log")
    
    if not os.path.exists(log_file):
        print(f"Không tìm thấy file log: {log_file}")
        print("Hãy chạy hệ thống trước để tạo log (bật 6 Node và thực hiện vài vòng Token).")
        return

    start_times = []
    end_times = []
    latencies = []

    # Đọc file log và trích xuất timestamp
    # Sử dụng errors="ignore" để bỏ qua các ký tự lỗi font
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "BENCHMARK_START:" in line:
                    match = re.search(r"BENCHMARK_START:([\d.]+)", line)
                    if match:
                        start_times.append(float(match.group(1)))
                elif "BENCHMARK_END:" in line:
                    match = re.search(r"BENCHMARK_END:([\d.]+)", line)
                    if match:
                        end_times.append(float(match.group(1)))
    except Exception as e:
        print(f"Lỗi khi đọc file log: {e}")
        return

    # Tính latency cho từng cặp start-end
    min_len = min(len(start_times), len(end_times))
    for i in range(min_len):
        latency = end_times[i] - start_times[i]
        if latency > 0:  # Chỉ lấy latency dương
            latencies.append(latency)

    if not latencies:
        print("Chưa có dữ liệu Latency. Hãy chạy hệ thống và thực hiện vài vòng Token.")
        return

    # Lấy đường dẫn tuyệt đối của thư mục chứa file benchmark.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    charts_dir = os.path.join(current_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # Vẽ biểu đồ
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(latencies) + 1), latencies, 
             marker='o', linestyle='-', color='r', label='Latency thực tế')
    
    plt.title('Biểu đồ Latency thực tế của Token Ring', fontsize=14)
    plt.xlabel('Số vòng', fontsize=12)
    plt.ylabel('Thời gian (giây)', fontsize=12)
    plt.grid(True)
    plt.legend()
    
    chart_path = os.path.join(charts_dir, "real_latency_chart.png")
    
    try:
        plt.savefig(chart_path)
        print(f"Đã lưu biểu đồ thực tế tại: {chart_path}")
    except Exception as e:
        print(f"Lỗi khi lưu biểu đồ: {e}")
    finally:
        plt.close()
    
    print("=" * 60)
    print("KẾT QUẢ ĐO LATENCY THỰC TẾ")
    print("=" * 60)
    print(f"Số vòng đo được: {len(latencies)}")
    print(f"Latency trung bình: {sum(latencies)/len(latencies):.4f} giây")
    print(f"Latency cao nhất: {max(latencies):.4f} giây")
    print(f"Latency thấp nhất: {min(latencies):.4f} giây")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmark()