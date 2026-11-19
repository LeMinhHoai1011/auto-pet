# Kết quả kiểm tra — 19/11/2026

**Cập nhật mới nhất:** luồng tự cho ăn đã chuyển sang kết hợp lịch + camera
xác nhận đứng chờ. Xem `VISION_FEEDING.md`; mô tả cửa sổ lịch cũ ở dưới
được thay bằng cửa sổ 30 phút, dwell 5 giây và lưu cữ đã xử lý vào NVS.
Hai bộ kiểm thử C++ về presence/window và lịch/NVS/reboot/reorder/write failure đạt.
Camera chưa có model hoặc vùng chờ đã hiệu chỉnh nên chưa kích hoạt tự nhả thực tế.

Sửa tiếp lỗi stale lock giả khi RTC/NTP chuyển giờ: RTC lưu giờ địa phương nhưng
epoch trả về được chuẩn hóa UTC; bộ đếm ngày dùng ngày địa phương. Tính tuổi thức
ăn/cooldown hiển thị chặn phép trừ không dấu khi giờ lùi. Nhả thất bại 0g không
ghi timestamp thức ăn mới. Test dùng chính timestamp `1795090887 -> 1795065764`
trong log đạt, cùng test mất giờ và tuổi thức ăn bình thường.

## Server

Docker Compose đã build và chạy đủ Mosquitto, PostgreSQL, FastAPI, Nginx.
Sửa file `server/mosquitto/passwd` từ plaintext sang hash bằng
`docker compose run --rm --no-deps mosquitto mosquitto_passwd -U /mosquitto/config/passwd`.
**Không chạy lại `-U` trên file đã hash.** File mật khẩu và `.env` là cấu hình local,
không commit. Khi triển khai máy khác cần tạo file password Mosquitto với tài khoản
khớp `MQTT_USER`/`MQTT_PASS` trong `.env`.

Đã kiểm tra 200 OK cho dashboard, docs, OpenAPI, health, device status,
schedule, feed history, alerts và sensors qua Nginx; MQTT echo có xác thực đạt.
Không gửi lệnh FEED/TARE đến thiết bị thật trong quá trình kiểm thử.

Chạy lại kiểm thử từ `server/`:

```powershell
docker compose cp tests/. api:/app/tests/
docker compose exec -T api python -m unittest discover -s tests -v
docker compose exec -T api python -m tests.smoke
```

Dashboard: http://localhost/ — API docs: http://localhost/docs

## Firmware

`pio run -e esp32dev -e esp32cam` thành công (camera dùng `HAS_TFLITE_MODEL=0`).
Firmware nhận cả `cmd`/`g` từ server và `command`/`amount` cũ.
`SCHEDULE` nhận tối đa 6 bữa `{h,m,g}`, kiểm tra toàn bộ trước khi áp dụng,
xóa các slot dư, lưu NVS; mảng rỗng tắt toàn bộ lịch. Giữ trạng thái đã cho ăn
theo giờ/phút khi thứ tự slot thay đổi. Server giới hạn khẩu phần 1–150g,
giờ/phút hợp lệ và tối đa 6 bản ghi lịch để khớp cấu hình firmware hiện tại.
Đã sửa server đọc `bowl_g`, `hopper_pct` và trạng thái `online`/`offline` từ firmware.

Chưa nạp lên board hoặc xác minh hoạt động cơ khí/NVS trên thiết bị thật.
Định dạng NVS lịch hiện tại vẫn là định dạng mới theo bản tóm tắt;
không bổ sung migration dữ liệu từ firmware cũ.
Lệnh lịch hiện gửi qua MQTT không retain, chưa có ACK/xác nhận áp dụng từ thiết bị;
thiết bị mất kết nối lúc chỉnh lịch có thể bỏ lỡ cập nhật.

## Model và Firebase

Chưa có dataset nên chưa train model. Đã thêm `ml/train.py` và `ml/README.md`
để train/evaluate/xuất int8 TFLite cùng header; kiểm tra cú pháp, CLI và báo thiếu
dữ liệu đạt. Chưa chạy TensorFlow training/conversion và chưa build chế độ TFLM.
Camera vẫn dùng phát hiện chuyển động. Firebase bỏ qua theo yêu cầu.

## Flutter

Đã sửa các cảnh báo dùng BuildContext sau await và cú pháp nullable widget.
`flutter analyze`: No issues found.
APK release tại `flutter_app/build/app/outputs/flutter-apk/app-release.apk`.
Cấu hình release hiện ký bằng debug key, dùng cho cài thử; chưa cấu hình khóa phát hành.
Trong Cài đặt của app, nhập IP LAN của máy server (không dùng localhost trên điện thoại).
Chưa cài APK lên điện thoại thật để kiểm thử.
