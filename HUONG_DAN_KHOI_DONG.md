# Hướng dẫn khởi động Pet-Auto trên Windows

Hệ thống chạy **trực tiếp trên Windows** bằng Python + Mosquitto, không cần
Docker, Ubuntu hay Nginx.

## Khởi động nhanh

```powershell
.\run.ps1
```

Script tự động: tạo virtual environment Python, cài dependencies, khởi động
Mosquitto MQTT broker và FastAPI server, rồi mở Dashboard trong trình duyệt.

## 1. Cài đặt yêu cầu

| Phần mềm | Phiên bản | Ghi chú |
|---|---|---|
| **Python** | 3.10+ | Thêm vào PATH khi cài |
| **Mosquitto** | 2.x | Tải từ [mosquitto.org/download](https://mosquitto.org/download/) |
| **VS Code** | mới nhất | Với extension PlatformIO IDE và Wokwi Simulator |

### Cài Mosquitto trên Windows

1. Tải installer từ [mosquitto.org/download](https://mosquitto.org/download/).
2. Cài đặt (mặc định `C:\Program Files\mosquitto`).
3. **Tắt Mosquitto Windows Service** (nếu tự khởi động):

   ```powershell
   net stop mosquitto
   sc config mosquitto start=disabled
   ```

   Script `run.ps1` sẽ tự khởi động Mosquitto với config riêng.

## 2. Cấu hình lần đầu

```powershell
if (!(Test-Path include/secrets.h)) {
    Copy-Item include/secrets.h.example include/secrets.h
}
```

File `server/.env` và `server/firebase-credentials.json` được tạo tự động
bởi `run.ps1` nếu chưa có.

### Thông tin MQTT

| File | Biến | Giá trị mặc định |
|---|---|---|
| `server/.env` | `MQTT_HOST` | `localhost` |
| `server/.env` | `MQTT_PORT` | `1883` |
| `include/secrets.h` | `MQTT_HOST` | `host.wokwi.internal` hoặc `localhost` |

Chế độ local dùng `allow_anonymous true` nên không cần tài khoản MQTT.

## 3. Địa chỉ truy cập

| Địa chỉ | Chức năng |
|---|---|
| `http://localhost:8000` | Web Dashboard |
| `http://localhost:8000/docs` | Swagger API (test REST API) |
| `http://localhost:8000/pet-demo` | Demo nhận dạng chó mèo |
| `localhost:1883` | MQTT Broker |

## 4. Cấu trúc hệ thống (Local)

```
ESP32 / Wokwi  ──MQTT──►  Mosquitto (localhost:1883)
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              FastAPI/Uvicorn      WebSocket /ws
            (localhost:8000)             │
                    │                     ▼
                    ▼              Web Dashboard
                 SQLite          (real-time update)
              petfeeder.db
```

## 5. Build firmware và chạy Wokwi

```powershell
pio run -e esp32dev
```

Hoặc dùng PlatformIO IDE trong VS Code: **Project Tasks → esp32dev → Build**.

Sau đó: **Ctrl+Shift+P → Wokwi: Start Simulator**.

### Cấu hình MQTT cho Wokwi

Trong `include/config.h`, giữ `WOKWI_SIM = 1`. Firmware sẽ dùng:
- WiFi: `Wokwi-GUEST`
- MQTT broker: `host.wokwi.internal:1883`

Wokwi gateway tự map `host.wokwi.internal` về `localhost` của máy host.

## 6. Chế độ DemoOnly

Chạy demo nhận dạng mà không cần MQTT hay server:

```powershell
.\run.ps1 -DemoOnly
```

## 7. Tham số run.ps1

| Tham số | Mô tả |
|---|---|
| (không) | Khởi động đầy đủ: Mosquitto + FastAPI + mở browser |
| `-DemoOnly` | Chỉ chạy web demo nhận dạng (port 8080) |
| `-NoBrowser` | Không tự mở trình duyệt |
| `-SkipMqtt` | Bỏ qua Mosquitto (nếu đã chạy sẵn) |

## 8. Dừng hệ thống

Nhấn `Ctrl+C` trong terminal đang chạy `run.ps1`.

## 9. Xử lý nhanh

| Hiện tượng | Giải pháp |
|---|---|
| `Mosquitto khong tim thay` | Cài Mosquitto và thêm vào PATH, hoặc dùng `-SkipMqtt` |
| Mosquitto thoát ngay | Cổng 1883 bị chiếm. Chạy `net stop mosquitto` tắt service |
| `pip install that bai` | Kiểm tra Python version (3.10+) và kết nối mạng |
| API không lên | Xem log terminal, kiểm tra `server/.env` |
| Dashboard trắng | Kiểm tra API health: `curl http://localhost:8000/api/health` |
| Wokwi không kết nối MQTT | Đảm bảo Mosquitto đang chạy và `WOKWI_SIM=1` |

## 10. Chế độ Docker (cũ)

Cấu hình Docker Compose vẫn được giữ tại `server/docker-compose.yml` cho
triển khai production. Để chạy bằng Docker:

```powershell
docker compose -f server/docker-compose.yml up -d --build
```

Lưu ý: cần đổi `DATABASE_URL` trong `.env` về PostgreSQL và `MQTT_HOST`
về `mosquitto` khi dùng Docker.

## 11. Phần chưa hoàn thiện

- Camera chưa có model YOLO được train cho pet detection thực tế.
- Firebase push notification chưa cấu hình.
- Flutter app cần cập nhật API endpoint sang `http://<IP>:8000`.
