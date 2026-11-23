# ĐỒ ÁN MÔN CÁC HỆ THỐNG PHÂN TÁN
# MÔ PHỎNG GIẢI THUẬT TOKEN RING

## 1. Giới thiệu
Đồ án mô phỏng hệ thống phân tán gồm 06 Node (0–5), giao tiếp qua TCP Socket và sử dụng giải thuật Token Ring để điều phối quyền truy cập tài nguyên dùng chung. Node chỉ được thực hiện thao tác thuộc vùng găng (Critical Section) khi nắm Token hợp lệ. Mục tiêu là minh họa Mutual Exclusion và hạn chế Race Condition/Lost Update.

Phạm vi hiện tại là mô hình đồ án. Không xem các cơ chế phục hồi là bảo đảm chịu được mọi kiểu lỗi mạng, phân hoạch mạng hoặc lỗi Byzantine.

## 2. Chức năng
- **Core:** khởi tạo Node, giao tiếp TCP, chuyển Token và bảo vệ vùng găng.
- **Watchdog:** theo dõi thời gian giữ Token; yêu cầu giải phóng khi quá hạn.
- **Token Lost:** phát hiện thời gian không quan sát thấy Token vượt ngưỡng.
- **Token Duplicate:** nhận diện Token khác UUID và xử lý theo quy tắc của chương trình.
- **Bypass:** thử chuyển Token sang Node khác khi Node kế tiếp không phản hồi.
- **Membership:** xử lý yêu cầu Node tham gia/rời vòng (JOIN/JOIN_ACK/LEAVE).
- **Lamport Clock:** ghi nhận thứ tự logic sự kiện.
- **Vector Clock:** hỗ trợ phân tích quan hệ nhân quả.
- **Applications:** File, Vote, Print, Blockchain và Game.
- **Dashboard/Logger:** tổng hợp log, trạng thái sống/chết qua heartbeat.
- **Benchmark:** đo Throughput, Latency từ log thực tế và tạo biểu đồ.
- **Mutex Proof:** chứng minh 3 tính chất Mutual Exclusion, No Deadlock, No Starvation từ log.

### Lưu ý về giới hạn chịu lỗi
Timeout không chứng minh Token chắc chắn đã mất; mạng chậm cũng có thể gây báo động giả. Nếu nhiều Node tự tạo Token sau timeout, có thể xuất hiện nhiều Token. UUID giúp nhận diện Token nhưng chỉ so sánh UUID không tự bảo đảm hội tụ toàn hệ thống. Muốn có bảo đảm mạnh hơn cần epoch/term và quy trình phục hồi có phối hợp.

Watchdog chỉ hoạt động khi luồng giám sát còn chạy; không thể cứu tiến trình bị kill, máy mất điện hoặc treo cứng toàn bộ.

## 3. Yêu cầu
- Python 3.10 trở lên.
- Windows, macOS hoặc Linux.
- Thư viện ngoài: `colorama`, `prompt_toolkit`, `reportlab`, `matplotlib`.

Cài đặt từ thư mục gốc:

```bash
python -m pip install -r requirements.txt
```

Nếu chưa có `requirements.txt`:

```bash
python -m pip install colorama prompt_toolkit reportlab matplotlib
```

Các module `socket`, `threading`, `json`, `time`, `uuid`, `os`, `queue` thuộc thư viện chuẩn Python.

## 4. Cấu hình
Ví dụ chạy 6 Node trên cùng một máy:

```python
TOTAL_NODES = 6
HOSTS = ["127.0.0.1"] * TOTAL_NODES
PORTS = [5001, 5002, 5003, 5004, 5005, 5006]
TOKEN_HOLD_TIMEOUT = 30
TOKEN_LOST_TIMEOUT = 30
SOCKET_TIMEOUT = 3
```

Tên biến phải khớp với `config.py` hiện tại. Khi chạy nhiều máy, thay `127.0.0.1` bằng IP LAN của từng máy, theo đúng thứ tự Node 0 đến Node 5. `127.0.0.1` chỉ dùng cho các tiến trình trên cùng máy.

Trên Windows, cho phép Python/các cổng TCP cần thiết qua Firewall trên mạng Private. Không nên tắt toàn bộ Firewall, nhất là trên mạng Public. Đảm bảo các máy cùng mạng có thể kết nối trực tiếp và cấu hình `HOSTS`/`PORTS` giống nhau.

## 5. Khởi chạy
Mở 6 cửa sổ Terminal/PowerShell. Trong mỗi cửa sổ, chuyển đến thư mục dự án:

```powershell
cd "C:\duong_dan\TokenRing_Project"
```

Chạy mỗi lệnh ở một cửa sổ riêng:

```powershell
python main.py 0
python main.py 1
python main.py 2
python main.py 3
python main.py 4
python main.py 5
```

Dashboard chạy độc lập ở cửa sổ thứ 7 (không bắt buộc, nhưng nên chạy để quan sát):

```powershell
python utils/log_viewer.py
```

Khi chạy nhiều máy, mỗi máy chạy đúng Node ID được phân công. Thứ tự khởi động phải phù hợp với logic JOIN và khởi tạo trong mã nguồn.

## 6. Lệnh tương tác
Gõ lệnh vào ô `NHAP DU LIEU` ở cuối màn hình mỗi Node, nhấn Enter.

| Lệnh | Chức năng |
| :--- | :--- |
| `VOTE A` / `VOTE B` | Bỏ phiếu cho A hoặc B |
| `PRINT` | Tạo PDF dữ liệu riêng của Node |
| `PRINT VOTE` | In lịch sử vote của Node |
| `GAME` | Tung xúc xắc, lưu kết quả chung + lịch sử riêng |
| `BLOCK <nội dung>` | Thêm block vào Blockchain |
| `TREO` | Mô phỏng Node bị treo cứng |
| Văn bản thường | Ghi vào file dùng chung + file riêng của Node |
| `Ctrl+C` | Dừng tiến trình Node |

## 7. Kịch bản kiểm thử

### 7.1 Mutual Exclusion
Gửi yêu cầu ghi từ hai Node gần như đồng thời (ví dụ: Node 0 gõ `hello`, Node 1 gõ `world` cùng lúc). Quan sát log vào/ra vùng găng và kiểm tra `shared_data/shared_data.txt`. Tiêu chí: không có hai Node cùng ở trong vùng găng tại một thời điểm.

### 7.2 Bypass
Dừng một Node trên đường chuyển Token (ví dụ: tắt Node 2 bằng `Ctrl+C`). Quan sát log Node 1 báo lỗi gửi, kích hoạt Bypass, chuyển Token sang Node 3. Kiểm tra cả trường hợp nhiều Node liên tiếp không phản hồi.

### 7.3 JOIN
Khởi động lại Node đã dừng. Quan sát thông điệp `JOIN` gửi đến Node trước, nhận `JOIN_ACK`, cập nhật `next_node`. Xác nhận Token tiếp tục đi theo vòng mới.

### 7.4 Token Lost/Duplicate
Tạo tình huống Token không được quan sát quá `TOKEN_LOST_TIMEOUT` (dừng tất cả Node, chỉ để 1 Node chạy, chờ 30s). Ghi nhận Node kích hoạt phục hồi, UUID được tạo. Nếu nhiều Node cùng tạo, kiểm tra log `"Phat hien Token trung"` và Token hợp lệ vẫn chạy vòng.

### 7.5 Watchdog
Gõ `TREO` ở một Node khi đang giữ Token. Xác nhận watchdog ghi cảnh báo `"Node dang treo cung, khong the giai phong"` và không giải phóng sai.

### 7.6 Ứng dụng
- **Vote:** gõ `VOTE A` ở nhiều Node, kiểm tra `shared_data/votes.json` và `shared_data/vote_history/node_*.json`.
- **Print:** gõ `PRINT`, kiểm tra file PDF trong `output/`.
- **Blockchain:** gõ `BLOCK test1`, `BLOCK test2`, kiểm tra `shared_data/blockchain.json` có liên kết Hash đúng.
- **Game:** gõ `GAME` ở nhiều Node, kiểm tra `shared_data/game_results.json`.
- **File:** gõ văn bản thường, kiểm tra `shared_data/shared_data.txt` và `shared_data/node_data/node_*.txt`.

### 7.7 Benchmark/Dashboard
Ghi rõ số Node, số request, số lần chạy, cấu hình máy và cách đo. Không tự đặt số liệu. Dashboard đọc log và heartbeat, hiển thị trạng thái `SONG`/`MAT KET NOI`.

## 8. Cấu trúc thư mục tham chiếu
```text
TokenRing_Project/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
├── core/
│   ├── __init__.py
│   ├── socket_handler.py
│   └── critical_section.py
├── fault_tolerance/
│   ├── __init__.py
│   ├── watchdog.py
│   ├── token_lost.py
│   ├── token_duplicate.py
│   ├── bypass.py
│   └── membership.py
├── distributed_properties/
│   ├── __init__.py
│   ├── lamport_clock.py
│   └── vector_clock.py
├── applications/
│   ├── __init__.py
│   ├── app_file.py
│   ├── app_vote.py
│   ├── app_print.py
│   ├── app_blockchain.py
│   └── app_game.py
├── shared_data/
├── output/
├── benchmark/
│   ├── __init__.py
│   ├── benchmark.py
│   ├── stress_test.py
│   ├── mutex_proof.py
│   └── charts/
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── ui.py
│   └── log_viewer.py
├── docs/
└── logs/
```

## 9. Giới hạn và lưu ý
- TCP bảo đảm truyền dữ liệu trong kết nối còn hoạt động, không tự bảo đảm Token logic không mất khi tiến trình dừng hoặc kết nối đứt.
- Timeout có thể báo lỗi giả khi mạng chậm.
- Bypass xử lý đường chuyển Token; Membership quản lý thành viên. Hai chức năng không đồng nhất.
- Watchdog trong tiến trình không cứu được tiến trình đã dừng hoàn toàn.
- Vector Clock có kích thước phụ thuộc số Node; không mặc nhiên suy rộng từ 6 lên 50 Node.
- Không kết luận hệ thống tốt hơn thuật toán khác nếu chưa có phép đo công bằng và dữ liệu thực tế.

## 10. Benchmark và chứng minh

### 10.1 Benchmark thực tế
Sau khi chạy 6 Node và gửi ít nhất 20 request (`VOTE`, `PRINT`, `GAME`, `BLOCK`, văn bản), chạy:

```bash
python benchmark/benchmark.py
```

Script đọc log thực từ `logs/node_*.log`, tính Throughput, Latency, xuất:
- `benchmark/charts/latency_real.png` — biểu đồ latency từng request
- `benchmark/charts/requests_per_node.png` — số request mỗi Node
- `benchmark/charts/benchmark_result.json` — kết quả tổng hợp

### 10.2 Chứng minh Distributed Mutex
```bash
python benchmark/mutex_proof.py
```

Kiểm tra 3 tính chất từ log:
- **Mutual Exclusion:** không có 2 Node cùng trong vùng găng.
- **No Deadlock:** có ít nhất 2 Node tham gia, Token vẫn chạy.
- **No Starvation:** số lần vào vùng găng giữa các Node tương đối đồng đều.

### 10.3 Phân tích ổn định
```bash
python benchmark/stress_test.py
```

Đọc log, đếm số lần gửi Token, Bypass, Token Lost, Token trùng → kết luận hệ thống ổn định hay không.

## 11. Kiểm tra sau khi chạy
1. Mở 6 terminal, chạy `python main.py 0` … `python main.py 5`.
2. Mở terminal thứ 7, chạy `python utils/log_viewer.py` — thấy Dashboard với 6 Node, trạng thái `SONG`, Token đang ở đâu.
3. Ở mỗi Node, gõ thử: `VOTE A`, `GAME`, `BLOCK test`, `hello`, `PRINT`.
4. Kiểm tra thư mục `shared_data/` có file `votes.json`, `game_results.json`, `blockchain.json`, `shared_data.txt`.
5. Kiểm tra thư mục `output/` có file PDF.
6. Chạy `python benchmark/benchmark.py` — thấy biểu đồ trong `benchmark/charts/`.
7. Chạy `python benchmark/mutex_proof.py` — thấy `PASS` cho Mutual Exclusion.
8. Tắt 1 Node (`Ctrl+C`), quan sát Node trước đó Bypass sang Node kế.

## 12. Thành viên
- **Nhóm:** 3
- **Môn học:** Các Hệ Thống Phân Tán
- **Giảng viên hướng dẫn:** Phạm Ngọc Bảo

| STT | Họ và tên | Mã sinh viên |
| :---: | :--- | :--- |
| 1 | Võ Văn Hoàng | N23DCCN090 |
| 2 | Lưu Gia Huy | N23DCCN094 |
| 3 | Nguyễn Lê Nhựt Hào | N23DCCN086 |
| 4 | Đinh Việt Hoàng | N23DCCN089 |
| 5 | Trần Minh Đức | N23DCCN080 |
| 6 | Nguyễn Đức Tâm | N23DCCN121 |