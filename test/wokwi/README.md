# Kiểm thử HX711 và motor trong Wokwi

Sửa sơ đồ: với `wokwi-esp32-devkit-v1`, GPIO16 có tên chân `RX2`, không phải
`D16`. Kết nối DT phải là `esp:RX2 -> hx711:DT`; SCK là `esp:D4 -> hx711:SCK`.
Tên `esp:D16` không hợp lệ có thể làm HX711 đọc 0 hoặc báo NOT READY.
Đã đối chiếu toàn bộ chân ESP32 trong sơ đồ với định nghĩa board Wokwi;
chưa chạy mô phỏng để xác nhận tải thực tế sau sửa.

Firmware `WOKWI_SIM=1` cho 30 giây chỉnh tải HX711 sau khi bắt đầu nhả.
Trong khoảng này chỉ tạm hoãn đếm lỗi jam/bridge; cân vẫn đọc thật từ mô phỏng,
đạt target vẫn dừng motor. Sau 30 giây bật lại kiểm tra lỗi. Timeout tổng 60 giây.
Đổi `WOKWI_FEED_GRACE_MS` ở `include/config.h` để thay thời gian thao tác.
Đặt 0 để thử lại ngưỡng phát hiện nhanh. Khi `WOKWI_SIM=0` không áp dụng grace.

## Thử bằng tay

1. Cân 0 kg trước boot; chờ tare và Ready.
2. Bấm nút một lần. Serial in `[TEST] HX711 ready`; OLED đếm giây còn lại.
3. Trong 30 giây, chỉnh tải 0.01 → 0.02 → 0.04 kg, mỗi mức chờ 3 giây.
4. Mong đợi `bowl`/`added` tăng, cuối cùng có `"type":"fed"` và motor dừng.
   0.04 kg dùng để chắc chắn vượt mốc 30g, không phải khẩu phần chính xác 30g;
   cân mô phỏng có độ phân giải hữu hạn và dữ liệu đi qua median filter.
5. Muốn thử lỗi: giữ nguyên 0 kg. Sau grace và 3 đợt không xuống hạt,
   mong đợi `bridge`, motor dừng. Nút tiếp theo xóa lỗi, không tự cho ăn lại.

Kiểm tra riêng cân không cần bấm: sau boot kéo lên 0.1 kg, chờ 3 giây,
OLED cần khoảng 100g. Nếu không đổi, cần sửa đường đọc cân trước.

## Kịch bản tự động (không cần kéo thanh)

Đã chuẩn bị hai scenario theo [Wokwi Automation Scenarios](https://docs.wokwi.com/wokwi-ci/automation-scenarios).
Chúng điều khiển tải cảm biến mô phỏng qua control `load` (kg), không sửa số gram
trong firmware. Máy hiện chưa có `wokwi-cli`, nên **chưa chạy hai scenario**.
Wokwi CLI cần cài đặt và license/token của bạn; thử mỗi scenario với bộ nhớ
mô phỏng mới, mặc định lịch/khẩu phần 30g, không giữ trạng thái cữ từ lần trước.

```powershell
pio run -e esp32dev
wokwi-cli . --scenario test/wokwi/feed-success.yaml --timeout 90000
wokwi-cli . --scenario test/wokwi/feed-no-food.yaml --timeout 90000
```

Scenario thứ nhất tăng cân tự động và chờ `fed`; thứ hai giữ cân 0, chờ `bridge`
và kiểm tra GPIO25 HIGH (driver disabled). Đây là kiểm thử cân/motor thủ công;
không xác nhận model camera, vùng chờ hoặc khả năng gỡ kẹt cơ khí thật.
