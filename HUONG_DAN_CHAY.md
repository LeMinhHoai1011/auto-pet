# Hướng dẫn chạy máy cho thú cưng ăn tự động

Tài liệu chia thành hai phần: **chạy lần đầu** và **khởi động những lần sau**. Các lệnh dưới đây chạy trong PowerShell, tại thư mục dự án có `platformio.ini`.

## 1. Chạy lần đầu

### 1.1. Chuẩn bị môi trường

1. Mở thư mục `pet-auto` bằng VS Code.
2. Cài extension PlatformIO IDE; nếu chạy mô phỏng thì cài thêm Wokwi for VS Code và hoàn tất đăng nhập/kích hoạt theo extension.
3. Mở **PlatformIO: New Terminal** từ Command Palette (`Ctrl+Shift+P`).
4. Kiểm tra CLI:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" --version
```

Nếu terminal thường báo không tìm thấy `pio`, dùng terminal của PlatformIO hoặc gọi trực tiếp:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" --version
```

Có thể thay `pio` trong các lệnh phía dưới bằng đường dẫn gọi trực tiếp này.

### 1.2. Chọn chế độ chạy

Sửa `include/config.h` theo chế độ cần dùng:

| Cấu hình | Mô phỏng Wokwi (mặc định) | ESP32 thật |
|---|---|---|
| `WOKWI_SIM` | `1` | `0` |
| `USE_WIFI` | `1` | `1` nếu cần web/NTP |
| `USE_WEBUI` | `1` | `1` nếu cần web |
| `USE_MQTT` | Giữ `0` khi chạy cơ bản | Giữ `0` khi chạy cơ bản |
| `USE_TELEGRAM` | Giữ `0` khi chạy cơ bản | Giữ `0` khi chạy cơ bản |

**Lưu ý về firmware hiện tại:**

- Wokwi tự kết nối `Wokwi-GUEST`, không cần mật khẩu hay `secrets.h` cho chế độ cơ bản.
- ESP32 thật hiện gọi `WiFi.begin()` để dùng thông tin WiFi đã lưu. Firmware chưa gọi WiFiManager và chưa đọc `WIFI_SSID`/`WIFI_PASSWORD` từ `secrets.h`. Bo mới chưa có thông tin WiFi cần bổ sung bước kết nối trong mã hoặc được cấu hình WiFi bằng chương trình khác trước; chỉ điền file secrets chưa đủ.
- Nếu cần chuẩn bị secrets, chạy lệnh dưới đây; lệnh giữ nguyên file đã có. Không chia sẻ thông tin bí mật:

```powershell
if (!(Test-Path include/secrets.h)) {
    Copy-Item include/secrets.h.example include/secrets.h
}
```

- Chưa bật MQTT/Telegram trong quy trình này: phần khai báo cấu hình trong `notify.cpp` chưa khớp file mẫu, lời gọi `queuePop` của MQTT chưa khớp API lưu trữ. MQTT nhận lệnh hiện chỉ ghi log; Telegram mới xử lý `/status` và `/help`, chưa xử lý `/feed`.

### 1.3. Build firmware

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e esp32dev
```

Chờ tải đủ thư viện và kết quả `[SUCCESS]`. Hai file dùng cho Wokwi là:

```text
.pio/build/esp32dev/firmware.bin
.pio/build/esp32dev/firmware.elf
```

`wokwi.toml` đã trỏ đến hai file này. Khi sửa mã hoặc cấu hình, phải build lại trước khi chạy.

### 1.4. Khởi chạy theo môi trường

**A. Mô phỏng Wokwi**

1. Mở `diagram.json` trong VS Code.
2. Nhấn `F1`, chọn **Wokwi: Start Simulator**.
3. Theo dõi Serial trong cửa sổ mô phỏng, tốc độ firmware là `115200`.
4. Tìm `[BOOT] Pet Feeder v2.0`, `[WebUI] started on port 80` và `[BOOT] Ready`.
5. Để HX711 ở mức bát rỗng khi khởi động vì firmware tự tare cân.

Servo trong Wokwi không tự làm giá trị HX711 tăng. Khi thử nhả, cần chủ động thay đổi tải HX711 theo thức ăn giả lập; nếu tải không tăng, firmware có thể báo `bridge` hoặc `jam`.

**B. ESP32 thật**

1. Tắt nguồn trước khi đấu dây; đối chiếu GPIO trong `include/config.h` và bảng phần cứng ở `README.md`.
2. Cấp nguồn riêng 5V tối thiểu 3A cho MG996R và nối chung GND với ESP32.
3. Đặt bát rỗng lên cân trước khi bật nguồn. Hệ số `LOADCELL_CALIBRATION = 420.0f` đang phục vụ mô phỏng; phải hiệu chỉnh bằng quả cân chuẩn cho loadcell thật.
4. Kết nối ESP32 với máy tính bằng cáp USB có truyền dữ liệu.
5. Tìm cổng:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" device list
```

6. Thay `COM5` bằng cổng thực tế, rồi nạp và xem log:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e esp32dev -t upload --upload-port COM5
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" device monitor --port COM5 --baud 115200
```

Nhấn `Ctrl+C` để thoát monitor. Đóng monitor trước khi nạp lại. Không cần chạy `uploadfs` cho giao diện web vì HTML nằm trong firmware; LittleFS được khởi tạo trong mã.

### 1.5. Kiểm tra từng quy trình sau khi khởi động

Thực hiện lần lượt, quan sát kết quả mỗi bước trước khi chuyển bước tiếp theo.

| Bước | Cách thực hiện | Kết quả cần kiểm tra |
|---|---|---|
| 1. Khởi động | Bật nguồn/chạy simulator, giữ bát rỗng | Có `[BOOT] Ready`; servo trở về góc đóng |
| 2. Đồng hồ | Kiểm tra RTC và giờ trên OLED | Giờ đúng GMT+7; nếu không có RTC thì cần WiFi/NTP để máy thoát trạng thái chờ giờ |
| 3. Cân | Đặt tải đã biết lên cân | Số gram tăng đúng; bỏ tải thì trở về gần 0 |
| 4. Thùng chứa | Thay khoảng cách HC-SR04 | Phần trăm thùng thay đổi, khoảng cách lớn hơn tương ứng thùng ít thức ăn hơn |
| 5. Môi trường | Thay nhiệt độ/độ ẩm DHT22 | Số đo cập nhật sau khoảng 10 giây |
| 6. Nhả bằng nút | Để máy ở trạng thái chờ, nhấn nút GPIO32 | Servo nhả theo khẩu phần lịch số 0 (mặc định 30g); log `[EVENT]` có `fed` khi cân tăng đủ |
| 7. Lịch ăn | Qua Web UI, đặt một cữ sau giờ hiện tại vài phút và lưu | Đến giờ máy xét nhả; chỉ xét trong 10 giây đầu của phút. Bát còn ít nhất 50% khẩu phần thì bỏ qua cữ |
| 8. PIR | Bát dưới 5g, kích PIR liên tục ít nhất 1 giây | Chỉ nhả khi giờ hợp lệ, ngoài 23:00–05:00, cách lần nhả trước ít nhất 2 giờ và chưa đạt giới hạn ngày |
| 9. Đổ bát | Nhấn “Đổ thức ăn thiu ngay” trên web và xác nhận | Servo bát nghiêng rồi trở về; kiểm tra bát thực sự đã sạch |
| 10. Khởi động lại | Đợi ít nhất 60 giây sau thay đổi dữ liệu vận hành rồi reset | Lịch đã lưu vẫn còn trên ESP32 thật; kiểm tra lại cân và giờ |

**Truy cập Web UI:** trên ESP32 thật đã vào WiFi, máy tính/điện thoại phải ở cùng mạng. Lấy IP từ danh sách thiết bị của router rồi mở `http://<IP-ESP32>/`. Có thể thử `http://petfeeder.local/`, nhưng mã hiện khởi tạo mDNS trước khi kết nối WiFi nên tên này có thể không hoạt động. Firmware hiện chưa in IP ra Serial.

Với Wokwi, việc truy cập web từ máy tính cần gateway/chuyển tiếp cổng phù hợp với môi trường Wokwi đang dùng; dự án chưa cấu hình chuyển tiếp cổng trong `wokwi.toml`. Không mặc định mở được IP nội bộ của mô phỏng từ trình duyệt máy tính.

Khi đã truy cập được thiết bị, có thể đọc trạng thái bằng PowerShell:

```powershell
# Thay bằng IP thật của ESP32
$feederUrl = 'http://192.168.1.123'
Invoke-RestMethod "$feederUrl/api/status"
Invoke-RestMethod "$feederUrl/api/schedule"
```

Lịch mặc định là **07:00 và 18:00, mỗi cữ 30g**, tối đa 6 mục lịch. Nút **Lưu lịch** ghi lịch vào NVS.

**Các điểm cần biết khi kiểm tra:**

- “Reset bát” hiện gọi cả `tareBowl()`: chỉ thực hiện khi bát rỗng. Nhãn trên web nói “vừa đổ thức ăn mới” có thể gây hiểu nhầm; tare khi bát còn thức ăn sẽ làm sai số cân.
- API/web nhả trực tiếp chưa dùng đầy đủ các kiểm tra giới hạn ngày và khóa thức ăn thiu của luồng chính. Chỉ thử từng lần có giám sát.
- Chế độ thức ăn thiu mặc định `AUTO_DISCARD_MODE = 0` chỉ cảnh báo; kiểm tra mỗi 30 phút, không tự đổ bát. Chế độ `1` chờ nhấn nút, chế độ `2` tự đổ; đổi chế độ cần build và nạp lại.
- Khi báo kẹt/vòm, xử lý nguyên nhân trước rồi nhấn nút để thoát trạng thái lỗi của luồng chính. Trong mô phỏng, kiểm tra đã tăng tải HX711 trong quá trình nhả chưa.
- Firmware chưa lưu cờ “cữ đã chạy” qua reset. Khởi động lại đúng 10 giây đầu của phút có lịch ăn có thể khiến cữ được xét lại.

## 2. Khởi động những lần sau

### 2.1. Chạy lại mô phỏng Wokwi

1. Mở thư mục dự án bằng VS Code.
2. Nếu không sửa mã và đã có firmware build thành công, bỏ qua bước build. Nếu có sửa hoặc thiếu file firmware, chạy:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e esp32dev
```

3. Đưa tải HX711 về bát rỗng trước lúc khởi động.
4. Mở `diagram.json`, nhấn `F1` → **Wokwi: Start Simulator**.
5. Kiểm tra `[BOOT] Ready`, giờ và cảm biến; thực hiện bài thử cần thiết ở mục 1.5.

Không cần cài lại extension/thư viện. Không mặc định NVS trong phiên mô phỏng mới giữ nguyên dữ liệu của phiên cũ; kiểm tra lại lịch khi mở lại simulator.

### 2.2. Bật lại ESP32 đã nạp firmware

1. Kiểm tra cơ cấu nhả, nguồn servo và lượng thức ăn trong thùng.
2. Đặt bát rỗng lên cân, rồi cấp nguồn ESP32 và nguồn servo. Firmware tự tare mỗi lần khởi động, kể cả sau mất điện; nếu bát đang có thức ăn, lấy thức ăn ra trước khi reset/cấp nguồn lại.
3. Chờ máy khởi động, kiểm tra giờ và số cân. Máy dùng WiFi đã lưu; lịch ăn được đọc từ NVS.
4. Mở lại địa chỉ IP của máy trên cùng mạng; kiểm tra router nếu IP thay đổi.
5. Xem lịch, cân và môi trường; sau đó cho máy chạy theo lịch đã lưu.

**Không cần build hoặc upload mỗi lần bật nguồn.** Chỉ nạp lại khi thay đổi firmware/cấu hình hoặc cần sửa lỗi. ESP32 đã nạp firmware có thể chạy bằng nguồn phù hợp mà không cần máy tính.

Nếu cần xem log, kết nối USB và chạy:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" device list
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" device monitor --port COM5 --baud 115200
```

Thay `COM5` bằng cổng thực tế. Nếu mở monitor làm bo reset, vẫn phải bảo đảm bát rỗng khi tare.

### 2.3. Khi chạy không thành công

| Hiện tượng | Việc cần làm |
|---|---|
| Không tìm thấy `pio` | Mở PlatformIO terminal hoặc dùng đường dẫn CLI tại mục 1.1 |
| Lỗi quyền `platforms.lock`/`.cache` | Chạy build trong môi trường có quyền ghi thư mục PlatformIO; không xóa cache để chữa lỗi quyền một cách tùy tiện |
| Build thất bại | Đọc lỗi `error:` đầu tiên; chưa chạy Wokwi/nạp firmware cho đến khi có `[SUCCESS]` |
| Không thấy cổng COM | Kiểm tra cáp dữ liệu, driver USB của bo, rút/cắm lại rồi chạy `& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" device list` |
| Không nạp được | Đóng Serial Monitor; kiểm tra đúng COM, thử giữ BOOT khi công cụ đang kết nối |
| Có Ready nhưng không chạy lịch/nút | Kiểm tra RTC/NTP; `[BOOT] Ready` chưa đảm bảo giờ đã hợp lệ |
| Không vào được web | Kiểm tra WiFi, cùng mạng và IP router; bo mới chưa có quy trình cấp WiFi trong firmware hiện tại |
| Cân luôn 0 hoặc lệch | Kiểm tra HX711, hiệu chỉnh hệ số và tare với bát rỗng |
| Máy reset lúc servo chạy | Kiểm tra nguồn servo riêng và nối chung GND |

### 2.4. Kết quả kiểm tra thực tế trong lần soạn tài liệu

- Đã build thành công (`[SUCCESS]`) môi trường mặc định `esp32dev` sau khi sửa lỗi mDNS: RAM 14,9%, Flash 72,6%; đã tạo `firmware.bin` và `firmware.elf`.
- Phát hiện và bỏ lời gọi `MDNS.update()` trong `src/webui.cpp` vì API ESP32 đang dùng không có hàm này.
- Lệnh liệt kê thiết bị không trả về cổng COM trong phiên kiểm tra.
- Các bước tương tác Wokwi, nạp ESP32, đo cảm biến và vận hành cơ khí là quy trình để thực hiện; chưa được xác nhận bằng chạy thiết bị trong phiên này.
