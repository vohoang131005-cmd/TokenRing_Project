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
- **Membership:** xử lý yêu cầu Node tham gia/rời vòng.
- **Lamport Clock:** ghi nhận thứ tự logic sự kiện.
- **Vector Clock:** hỗ trợ phân tích quan hệ nhân quả.
- **Applications:** File, Vote, Print, Blockchain và Game.
- **Dashboard/Logger:** tổng hợp log và trạng thái quan sát.
- **Benchmark:** đo Throughput, Latency và tạo biểu đồ từ dữ liệu chạy thực tế.

### Lưu ý về giới hạn chịu lỗi
Timeout không chứng minh Token chắc chắn đã mất; mạng chậm cũng có thể gây báo động giả. Nếu nhiều Node tự tạo Token sau timeout, có thể xuất hiện nhiều Token. UUID giúp nhận diện Token nhưng chỉ so sánh UUID không tự bảo đảm hội tụ toàn hệ thống. Muốn có bảo đảm mạnh hơn cần epoch/term và quy trình phục hồi có phối hợp.

Watchdog chỉ hoạt động khi luồng giám sát còn chạy; không thể cứu tiến trình bị kill, máy mất điện hoặc treo cứng toàn bộ.

## 3. Yêu cầu
- Python 3.10 trở lên.
- Windows, macOS hoặc Linux.
- Thư viện ngoài: `colorama`, `prompt_toolkit`, `reportlab`, `matplotlib`.

Cài đặt từ thư mục gốc:

```bash
python -m pip install colorama prompt_toolkit reportlab matplotlib
```

Nếu có `requirements.txt`:

```bash
python -m pip install -r requirements.txt
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

Trên Windows, cho phép Python/các cổng TCP cần thiết qua Firewall trên mạng **Private**. Không nên tắt toàn bộ Firewall, nhất là trên mạng Public. Đảm bảo các máy cùng mạng có thể kết nối trực tiếp và cấu hình HOSTS/PORTS giống nhau.

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

Nếu Dashboard hỗ trợ chạy độc lập:

```powershell
python utils/log_viewer.py
```

Khi chạy nhiều máy, mỗi máy chạy đúng Node ID được phân công. Thứ tự khởi động phải phù hợp với logic JOIN và khởi tạo trong mã nguồn. Việc khởi động trong 3–5 giây không phải yêu cầu của thuật toán, trừ khi code hiện tại có quy định riêng.

## 6. Lệnh tương tác
Các lệnh dưới đây là cú pháp dự kiến theo chức năng mô tả; cần đối chiếu parser trong `main.py` trước khi demo.

| Lệnh | Chức năng |
|---|---|
| `VOTE A` / `VOTE B` | Bỏ phiếu |
| `PRINT` | Tạo PDF dữ liệu Node |
| `PRINT VOTE` | In lịch sử vote nếu được hỗ trợ |
| `GAME` | Chơi/tung xúc xắc |
| `BLOCK <nội dung>` | Thêm dữ liệu vào Blockchain |
| `TREO` | Mô phỏng tình huống treo nếu được cài đặt |
| Văn bản thường | Ghi dữ liệu dùng chung nếu được hỗ trợ |
| `Ctrl+C` | Dừng tiến trình Node |

## 7. Kịch bản kiểm thử
### 7.1 Mutual Exclusion
Gửi yêu cầu ghi từ hai Node gần như đồng thời. Quan sát log vào/ra vùng găng và kiểm tra tệp dùng chung. Tiêu chí: không có hai Node cùng ở trong vùng găng tại một thời điểm.

### 7.2 Bypass
Dừng một Node trên đường chuyển Token. Quan sát lỗi gửi TCP, Node bị bỏ qua và tuyến vòng mới. Kiểm tra cả trường hợp nhiều Node liên tiếp không phản hồi.

### 7.3 JOIN
Khởi động một Node mới hoặc bật lại Node đã dừng. Quan sát thông điệp JOIN, kiểm tra Node trùng và xác nhận Token tiếp tục đi theo vòng mới. Nếu code chỉ hỗ trợ JOIN cơ bản, ghi rõ giới hạn.

### 7.4 Token Lost/Duplicate
Tạo tình huống Token không được quan sát quá `TOKEN_LOST_TIMEOUT`. Ghi nhận Node kích hoạt phục hồi, UUID được tạo và kiểm tra toàn vòng xem có nhiều Token hay không. Một lần chạy thành công chưa đủ chứng minh bảo đảm duy nhất.

### 7.5 Watchdog
Tạo tình huống giữ Token quá thời gian cho phép. Xác nhận watchdog còn hoạt động, ghi cảnh báo và thực hiện hành động giải phóng theo thiết kế.

### 7.6 Ứng dụng
- Vote: kiểm tra tổng phiếu và lịch sử.
- Print: kiểm tra PDF được tạo và mở được.
- Blockchain: kiểm tra liên kết Hash giữa các block.
- Game: kiểm tra lệnh và kết quả.
- File: gửi yêu cầu từ nhiều Node, kiểm tra dữ liệu và thứ tự ghi.

### 7.7 Benchmark/Dashboard
Ghi rõ số Node, số request, số lần chạy, cấu hình máy và cách đo. Không tự đặt số liệu. Dashboard phải đọc đúng nguồn log/trạng thái và xử lý được file chưa tồn tại hoặc dữ liệu đang ghi dở.

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
│   └── charts/
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── ui.py
│   └── log_viewer.py
├── docs/
└── logs/
```

Đây là cây tham chiếu. Nếu class `Node` đang nằm trong `main.py`, không bắt buộc tạo `core/node.py`. Nếu tách class ra, phải cập nhật import. File JSON, PDF, log và biểu đồ có thể được sinh tự động khi chạy.

## 9. Giới hạn và lưu ý
1. TCP bảo đảm truyền dữ liệu trong kết nối còn hoạt động, không tự bảo đảm Token logic không mất khi tiến trình dừng hoặc kết nối đứt.
2. Timeout có thể báo lỗi giả khi mạng chậm.
3. Bypass xử lý đường chuyển Token; Membership quản lý thành viên. Hai chức năng không đồng nhất.
4. Watchdog trong tiến trình không cứu được tiến trình đã dừng hoàn toàn.
5. Vector Clock có kích thước phụ thuộc số Node; không mặc nhiên suy rộng từ 6 lên 50 Node.
6. Không kết luận hệ thống tốt hơn thuật toán khác nếu chưa có phép đo công bằng và dữ liệu thực tế.

## 10. Thành viên
**Nhóm:** 3

| STT | Họ và tên | Mã sinh viên |
|---:|---|---|
| 1 | Võ Văn Hoàng | N23DCCN090 |
| 2 | Lưu Gia Huy | N23DCCN094 |
| 3 | Nguyễn Lê Nhựt Hào | N23DCCN086 |
| 4 | Đinh Việt Hoàng | N23DCCN089 |
| 5 | Trần Minh Đức | N23DCCN080 |
| 6 | Nguyễn Đức Tâm | N23DCCN121 |

**Môn học:** Các Hệ Thống Phân Tán  
**Giảng viên hướng dẫn:** Phạm Ngọc Bảo
