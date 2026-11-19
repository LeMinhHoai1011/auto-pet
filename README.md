# Máy cho thú cưng ăn tự động — Nhóm 18 Đề tài 7

Firmware ESP32 cho máy cho thú cưng ăn hạt khô tự động. Hỗ trợ lịch ăn theo giờ, phát hiện thức ăn thiu, cảnh báo qua Telegram/MQTT, giao diện web, và mô phỏng Wokwi.

---

## Phần cứng

| Linh kiện | Chân ESP32 |
|---|---|
| Servo nhả thức ăn (MG996R) | GPIO 13 |
| Servo bát nghiêng (MG90S) | GPIO 33 |
| HX711 DT / SCK | GPIO 16 / 4 |
| HC-SR04 TRIG / ECHO | GPIO 5 / 18 |
| DHT22 | GPIO 15 |
| PIR | GPIO 19 |
| Nút thủ công | GPIO 32 |
| Buzzer | GPIO 23 |
| LED trạng thái | GPIO 2 |
| OLED SSD1306 + RTC DS1307 (I2C) | SDA 21 / SCL 22 |

> **Quan trọng:** Servo MG996R phải dùng nguồn 5V riêng (≥3A). Nối chung GND với ESP32. Dùng nguồn 5V từ chân ESP32 sẽ gây brownout.

---

## Cài đặt

### 1. Clone & cài PlatformIO

```bash
git clone <repo-url>
cd pet-auto
```

Cài [PlatformIO](https://platformio.org/) cho VS Code hoặc dùng CLI.

### 2. Tạo file secrets

```bash
cp include/secrets.h.example include/secrets.h
```

Chỉnh sửa `include/secrets.h` với thông tin WiFi, MQTT, Telegram của bạn.

> **Không commit `secrets.h` lên git.** File này đã được `.gitignore`.

### 3. Build & Upload

```bash
pio run -t upload
```

### 4. Mô phỏng Wokwi

Cài extension [Wokwi for VS Code](https://marketplace.visualstudio.com/items?itemName=wokwi.wokwi-vscode), sau đó nhấn `F1` → `Wokwi: Start Simulator`.

```bash
pio run   # build firmware trước
```

---

## Cấu hình (`include/config.h`)

| Hằng số | Mặc định | Mô tả |
|---|---|---|
| `AUTO_DISCARD_MODE` | 0 | 0=cảnh báo, 1=chờ nút, 2=tự động |
| `FEED_COOLDOWN_S` | 7200 | Cooldown giữa 2 lần nhả (s) |
| `DAILY_MAX_FEEDS` | 6 | Số cữ tối đa / ngày |
| `DAILY_MAX_GRAMS` | 150 | Gram tối đa / ngày |
| `STALE_BASE_H` | 12 | Giờ trước khi thức ăn bị coi là thiu |
| `WOKWI_SIM` | 1 | 1=Wokwi, 0=phần cứng thật |

---

## Các module

```
src/
  main.cpp      — Máy trạng thái chính (INIT→IDLE→FEEDING→STALE_ALERT→DISCARD)
  sensors.cpp   — HX711, HC-SR04, DHT22, PIR, stalenessScore()
  feeder.cpp    — Nhả thức ăn, phát hiện kẹt/vòm, đổ bát
  schedule.cpp  — Lịch 6 cữ, lưu NVS
  timekeeper.cpp— NTP + RTC DS1307 backup
  storage.cpp   — NVS (Preferences) + LittleFS offline queue
  display.cpp   — OLED SSD1306
  webui.cpp     — Web UI + REST API
  notify.cpp    — MQTT + Telegram
```

---

## Web UI

Sau khi kết nối WiFi, mở trình duyệt:
- **LAN IP**: địa chỉ IP hiện trên Serial monitor
- **mDNS**: `http://petfeeder.local` (macOS/Linux/Windows 10+)

### REST API

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/status` | GET | Trạng thái hiện tại (bát, thùng, nhiệt độ...) |
| `/api/feed` | POST | Nhả thức ăn — body: `{"grams":30}` |
| `/api/schedule` | GET | Lấy danh sách lịch |
| `/api/schedule` | POST | Cập nhật lịch |
| `/api/bowl-reset` | POST | Reset bát (vừa đổ thức ăn mới thủ công) |
| `/api/discard` | POST | Đổ thức ăn thiu ngay lập tức |

---

## MQTT Topics

Prefix: `petfeeder/device01/`

| Topic | Hướng | Nội dung |
|---|---|---|
| `cmd/feed` | ← | `{"grams":30}` |
| `cmd/schedule` | ← | JSON lịch (retained) |
| `cmd/discard` | ← | `{}` |
| `cmd/bowl-reset` | ← | `{}` |
| `event` | → | JSON sự kiện |
| `status` | → | `online` / `offline` (LWT) |

### Sự kiện

| type | Mô tả |
|---|---|
| `fed` | Nhả thành công |
| `skipped` | Bỏ qua cữ (bát còn đầy) |
| `jam` | Kẹt motor |
| `bridge` | Vòm thức ăn trong thùng |
| `stale_discard` | Đổ thức ăn thiu |
| `not_eaten` | Thức ăn không giảm sau 4h |
| `hopper_low` | Thùng < 20% |
| `humidity_high` | Độ ẩm > 70% |
| `pet_refusing` | PIR kích nhưng thú cưng không ăn ≥2 lần |
| `interrupted_feed` | Mất điện giữa nhả |

---

## Phát hiện thức ăn thiu

Điểm thiu (`stalenessScore`):
- Tính theo thời gian từ lần nhả cuối, điều chỉnh theo độ ẩm và nhiệt độ
- Điểm ≥ 1.0: cảnh báo / kích đổ (tùy `AUTO_DISCARD_MODE`)
- Điểm ≥ 1.5: khóa không nhả thêm cho đến khi reset bát

```
Môi trường bình thường (hum < 60°, temp < 30°C): ngưỡng 12h
Độ ẩm 60–70%: ngưỡng 8h
Độ ẩm > 70%: ngưỡng 4h
Nhiệt độ > 30°C: nhân 0.75 vào ngưỡng
Thú cưng ngửi rồi bỏ ≥2 lần: +1.0 điểm
```

---

## Giới hạn đã biết

- Thú cưng hất thức ăn ra sàn → loadcell giảm sai số → chấp nhận được
- Không phân biệt được nhiều thú cưng khác nhau (cần RFID/camera AI cho đa thú)
- Chỉ hỗ trợ thức ăn hạt khô (dry food), không hỗ trợ pate/wet food
- OTA firmware update: để giai đoạn 3+

---

## Giấy phép

MIT © Nhóm 18 — Đề tài 7
