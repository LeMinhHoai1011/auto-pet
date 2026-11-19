# Hướng dẫn chạy Docker, web và mạch Wokwi

Áp dụng cho **Windows + PowerShell + VS Code**. Đây là file hướng dẫn thao tác,
không phải script tự chạy. Thực hiện từ trên xuống trong lần đầu; những lần sau
chỉ cần phần **Khởi động hằng ngày**.

## 1. Chuẩn bị

Cài sẵn:

- Docker Desktop, mở ứng dụng và chờ engine hoạt động.
- VS Code với extension **PlatformIO IDE** và **Wokwi Simulator**.
- License Wokwi còn hiệu lực hoặc trial; nhập trực tiếp trong VS Code khi được yêu cầu.

Mở **File → Open Folder** trong VS Code và chọn thư mục chứa `platformio.ini`,
`diagram.json`, `wokwi.toml`, `src/`, `server/`. Không mở riêng thư mục `src/`.

Nếu tải mới từ GitHub:

```powershell
git clone https://github.com/LeMinhHoai1011/auto-pet.git
cd auto-pet
code .
```

Trong VS Code chọn **Terminal → New Terminal**. Các lệnh dưới dùng PowerShell.
Nếu dùng thư mục hiện có `pet-auto`, không cần clone lại.

## 2. Tạo cấu hình local — chỉ lần đầu

Chạy tại thư mục gốc dự án. Không ghi đè cấu hình đang dùng:

```powershell
if (!(Test-Path include/secrets.h)) {
    Copy-Item include/secrets.h.example include/secrets.h
}
if (!(Test-Path server/.env)) {
    Copy-Item server/.env.example server/.env
}
if (!(Test-Path server/firebase-credentials.json)) {
    Set-Content server/firebase-credentials.json '{}' -Encoding ascii
}
```

Firebase hiện bỏ qua; `{}` chỉ là file placeholder để Docker mount được,
không bật được push notification.

Kiểm tra tài khoản MQTT trong hai file phải khớp nhau:

| Cấu hình | Giá trị mặc định để thử local |
|---|---|
| `server/.env`: `MQTT_USER` | `mqtt_user` |
| `server/.env`: `MQTT_PASS` | `mqtt_pass` |
| `include/secrets.h`: `MQTT_USER` | `mqtt_user` |
| `include/secrets.h`: `MQTT_PASS` | `mqtt_pass` |

Trong `include/config.h`, giữ `WOKWI_SIM = 1` (dòng `#define WOKWI_SIM 1`).
Ở chế độ này firmware dùng WiFi `Wokwi-GUEST` và broker
`host.wokwi.internal:1883` để truy cập máy chạy gateway Wokwi.

Các mật khẩu mặc định chỉ phục vụ chạy local. Nếu đổi mật khẩu, đồng bộ
`server/.env`, `include/secrets.h` và file mật khẩu Mosquitto.
Không commit những file cấu hình riêng này lên GitHub.

### Tạo mật khẩu Mosquitto

Từ thư mục gốc, vào `server/`:

```powershell
cd server
docker info
docker compose version
```

Chỉ chạy lệnh sau **khi chưa có file `mosquitto/passwd`**. Nếu đã có file hash
đang hoạt động, giữ nguyên. `-c` tạo mới và có thể ghi đè danh sách tài khoản:

```powershell
docker run --rm --mount "type=bind,source=$((Get-Location).Path)\mosquitto,target=/mosquitto/config" --entrypoint mosquitto_passwd eclipse-mosquitto:2 -c -b /mosquitto/config/passwd mqtt_user mqtt_pass
```

Lệnh dùng tài khoản mặc định ở bảng trên. Nếu đã đổi thông tin MQTT, thay hai
tham số cuối bằng thông tin tương ứng. File `passwd` phải chứa hash do công cụ
tạo ra; không tự nhập dòng `mqtt_user:mqtt_pass` dạng văn bản thường.

## 3. Khởi động server và mở web

Vẫn ở `server/`:

```powershell
docker compose up -d --build
docker compose ps
```

Cần thấy cả bốn service `mosquitto`, `db`, `api`, `nginx` đang chạy.
Chờ API khởi động, sau đó kiểm tra:

```powershell
Invoke-RestMethod http://localhost/api/health
Start-Process 'http://localhost/'
```

| Địa chỉ | Nội dung |
|---|---|
| <http://localhost/> | Dashboard điều khiển và theo dõi |
| <http://localhost/docs> | Tài liệu/test REST API |
| <http://localhost/api/device/status> | Trạng thái ESP32 đã lưu trong server |

`/api/health` trả về `status: ok` chỉ xác nhận API hoạt động.
`/api/device/status` trả `null` nghĩa là server chưa có trạng thái thiết bị;
không có nghĩa ESP32 đã kết nối thành công.

## 4. Build firmware và hiển thị mạch

Quay về gốc dự án từ `server/`:

```powershell
cd ..
pio run -e esp32dev
```

Nếu PowerShell báo không tìm thấy `pio`, dùng bản PlatformIO do VS Code cài:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run -e esp32dev
```

Hoặc chọn **PlatformIO → Project Tasks → esp32dev → General → Build**.
Đợi kết quả `SUCCESS`.

Sau đó:

1. Mở `diagram.json` trong Explorer của VS Code để xem sơ đồ.
2. Nhấn **Ctrl+Shift+P**, chọn **Wokwi: Start Simulator**.
3. Nếu được hỏi license, hoàn tất bước đó trong Wokwi.
4. Chờ OLED và Serial xuất hiện. Giữ tab mô phỏng hiển thị trong lúc thử.

`wokwi.toml` đã trỏ đến `.pio/build/esp32dev/firmware.bin` và `firmware.elf`.
Mạch đang mô phỏng máy cho ăn ESP32, không phải camera ESP32-CAM.
Firmware bỏ qua LittleFS trong Wokwi; `[QUEUE] skip (no LittleFS)` là thông báo
không lưu hàng đợi offline trong chế độ này.

Sau khi sửa `diagram.json`, dừng rồi chạy lại mô phỏng để tải kết nối mới.
Sau khi sửa C++, build lại trước khi chạy mô phỏng.

## 5. Kiểm tra cân trước, chưa bấm cho ăn

1. Đặt thanh Pressure của HX711 ở **0 kg** trước khi khởi động.
2. Chờ `[SENSOR] HX711 tare OK` và `[BOOT] Ready`.
3. Không bấm nút cho ăn. Bấm cảm biến HX711, tăng Pressure lên **0,1 kg**.
4. Chờ khoảng 3 giây cho bộ lọc ổn định.

Mong đợi:

- Serial: `[HX711] ... factor=0.42 grams=...` gần **100g**.
- OLED: `Bat:...g` gần **100g**.
- Có dòng `[MQTT TX] ... payload={"bowl_g":...}`.

`tare` là mốc trừ bì. Nếu khởi động khi cân đã có tải, lượng đó trở thành mốc 0;
số gram hiển thị là phần chênh so với mốc, không phải toàn bộ tải trên thanh.

Kết nối đúng trong `diagram.json`:

```json
["esp:RX2", "hx711:DT", "green", []],
["esp:D4", "hx711:SCK", "blue", []]
```

GPIO16 trên board `wokwi-esp32-devkit-v1` có tên **RX2**, không phải D16.

## 6. Kiểm tra dữ liệu lên dashboard

Để mô phỏng tiếp tục chạy, mở dashboard rồi nhấn **Ctrl+F5** để tải giao diện mới.
Firmware gửi trạng thái khi kết nối MQTT và định kỳ khoảng 5 giây;
dashboard làm mới mỗi 5 giây khi vòng firmware hoạt động bình thường.

Kiểm tra API từ terminal đang ở gốc dự án:

```powershell
Invoke-RestMethod http://localhost/api/device/status
```

Khi đã nhận dữ liệu, phản hồi có `bowl_grams` khớp gần với OLED.
Nếu OLED đổi nhưng API vẫn `null`, kiểm tra đường MQTT bằng log server:

```powershell
docker compose -f server/docker-compose.yml logs --tail 80 api mosquitto
```

Serial ESP32 cần có `[MQTT] connected remote=...:1883`.
Log Mosquitto local cần có kết nối của client `device01` và dữ liệu ở topic
`petfeeder/device01/sensor/weight`. `sent` trong Serial chỉ xác nhận gửi vào
kết nối MQTT hiện tại, không chứng minh server local đã lưu dữ liệu.

## 7. Test web gửi lệnh về ESP32

### Test STATUS, không quay motor

Từ gốc dự án, sao chép probe rồi chạy trong container:

```powershell
docker compose -f server/docker-compose.yml cp server/tests/probe_status.py api:/app/probe_status.py
docker compose -f server/docker-compose.yml exec -T api python /app/probe_status.py
```

Probe yêu cầu thiết bị gửi trạng thái rồi đọc lại API, không thay đổi tải cân.
ESP32 cần xuất hiện:

```text
[MQTT] RX petfeeder/device01/command: {"cmd": "STATUS"}
```

Nếu `STATUS published: True` nhưng không có dòng RX và trạng thái vẫn `null`,
chưa xác nhận được kết nối hai chiều. Cần xử lý broker/gateway trước khi thử motor.

### Test cho ăn 30g

1. Đưa cân về **0 kg**, chờ OLED ổn định gần 0g. Nếu mốc tare không còn đúng,
   khởi động lại với cân 0 kg trước khi thử.
2. Trên dashboard chọn **30g** rồi bấm **Cho ăn** một lần.
3. Serial phải có `[MQTT] RX ... {"cmd":"FEED","g":30}` (khoảng trắng có thể khác).
4. Khi `[TEST] HX711 ready` xuất hiện, tăng tải **0,01 → 0,02 → 0,04 kg**;
   mỗi mức giữ khoảng 3 giây.
5. Mong đợi motor dừng, log có `"type":"fed","src":"remote"`.

Mô phỏng hiện cho **30 giây** chỉnh tải trước khi kiểm tra kẹt/không xuống hạt;
đạt lượng cần nhả vẫn dừng ngay, timeout tổng khoảng **60 giây**.
Mốc 0,04 kg được dùng để chắc chắn vượt 30g khi kiểm thử; không phải khẳng định
khẩu phần ra đúng 30g. Cân mô phỏng có độ phân giải hữu hạn.

Motor Wokwi không tự làm tải HX711 tăng. Kéo thanh chỉ mô phỏng thức ăn rơi xuống
trong bài test, không phải bước cần làm trên máy cho ăn thật.

**Web báo đã gửi tới broker chưa phải xác nhận motor đã chạy.**
`"src":"manual"` là nút trên mạch; `"src":"remote"` là lệnh từ app/web.
Nếu bát đã có 78g hoặc 140g mà chọn mục tiêu 30g, máy bỏ qua (`skipped`) vì
không cần bổ sung. Giá trị trên web hiện là mục tiêu lượng trong bát, không phải
lúc nào cũng nhả thêm đúng số gram đó.

## 8. Test lỗi không xuống hạt

Sau khi kiểm tra kết nối/cân thành công:

1. Cho cân về 0 kg và bắt đầu một lần cho ăn.
2. Giữ nguyên cân 0 kg.
3. Sau 30 giây chờ thao tác và ba đợt không xuống hạt, mong đợi `bridge`.
4. Motor phải dừng, OLED báo lỗi và MQTT gửi cảnh báo.
5. Kiểm tra rồi nhấn nút một lần để xóa lỗi; thao tác xóa lỗi không tự nhả lại.

Encoder đang được giả lập trong Wokwi nên bài test này không xác minh được
kẹt trục thật. Hai scenario tự động và cách chạy bằng Wokwi CLI được ghi tại
[`test/wokwi/README.md`](test/wokwi/README.md); các scenario chưa được chạy xác minh.

## 9. Khởi động hằng ngày

Sau lần thiết lập đầu, chỉ cần:

1. Mở Docker Desktop và chờ engine sẵn sàng.
2. Tại gốc dự án chạy:

   ```powershell
   docker compose -f server/docker-compose.yml up -d --build
   pio run -e esp32dev
   Start-Process 'http://localhost/'
   ```

3. Trong VS Code chọn **Wokwi: Start Simulator** để mở mạch.
4. Kiểm tra cân, MQTT và API trước khi thử cho ăn.

Để dừng server nhưng giữ database:

```powershell
docker compose -f server/docker-compose.yml stop
```

Không dùng `down -v` trong thao tác dừng thường ngày vì tùy chọn đó xóa volume dữ liệu.

## 10. Xử lý nhanh

| Hiện tượng | Kiểm tra |
|---|---|
| Docker không kết nối được | Mở Docker Desktop, kiểm tra `docker info`. |
| Mosquitto liên tục restart | Kiểm tra file hash `server/mosquitto/passwd` và log broker. |
| API chưa lên ngay lần đầu | Xem `docker compose ... logs api db`; database có thể đang khởi tạo. Chờ rồi kiểm tra health lại. |
| Web báo 502 sau build lại API | Chạy `docker compose -f server/docker-compose.yml restart nginx`, rồi kiểm tra health. |
| `HX711 NOT READY` | Kiểm tra nguồn, GND, DT → RX2, SCK → D4; chạy lại sơ đồ mới. |
| `raw=0` dù firmware chạy | Xác nhận đã tăng đúng thanh Pressure của HX711; thử cân riêng trước khi bấm. |
| OLED có gram, web không có | Kiểm tra MQTT hai chiều, broker thực tế và API status; không tự coi `sent` là xác nhận lưu DB. |
| Motor quay, cân không tăng | Wokwi chưa mô phỏng hạt rơi; tăng tải HX711 trong khoảng chờ test. |
| `skipped` | Bát có thể đã đủ mục tiêu hoặc bị stale lock; xem dòng ngay trước sự kiện. |
| `[HX711]`/`[MQTT TX]` in lặp | Đây là log đọc/gửi trạng thái định kỳ, không có nghĩa motor quay liên tục. |
| Không thấy biểu đồ | Kiểm tra kết nối Internet để tải Chart.js từ CDN và đã có dữ liệu cảm biến hay chưa. |

## 11. Phần chưa hoàn thiện

Camera chưa có model được train hoặc vùng chờ được hiệu chỉnh, nên chưa kích hoạt
tự nhả thực tế. Luồng tự động có điều kiện cữ ăn, đứng chờ và chống nhả lặp,
nhưng không thể kiểm thử nhận diện thú bằng mạch Wokwi hiện tại.
Xem [`VISION_FEEDING.md`](VISION_FEEDING.md).

Firebase chưa cấu hình. Flutter là phần riêng, không bắt buộc để hiển thị mạch
và dashboard. APK không nằm trong Git; cần build riêng khi muốn dùng điện thoại.
