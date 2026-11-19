# Tự cho ăn khi thú đứng chờ

Theo yêu cầu, cho ăn **tự động**, không cần bấm xác nhận.

Chỉ nhả khi đồng thời:

- Có cữ đang đến hạn: từ giờ hẹn đến trước 30 phút sau đó.
- Cữ đó chưa được xử lý trong ngày.
- Camera liên tục gửi mèo/chó trong vùng chờ, confidence 0–1 từ 0.70 trở lên,
  ít nhất 5 giây, khoảng cách giữa hai bản tin tối đa 1.5 giây.
- Bản tin gần nhất chưa quá 1.5 giây, bát dưới 5g, hết cooldown,
  không bị khóa thức ăn cũ, còn giới hạn khẩu phần/ngày.

Đi ngang, ra khỏi vùng, mất camera hoặc thiếu `in_zone` đều không kích hoạt.
Đúng giờ mà chưa có thú thì chờ trong cửa sổ cữ; camera thấy thú ngoài cửa sổ
cũng không nhả. Mỗi cữ được ghi vào NVS theo ngày và giờ/phút **trước khi quay motor**.
Khởi động lại, đảo thứ tự lịch hoặc tháo/thêm lại cùng giờ không tạo cữ thứ hai.
Kẹt hoặc mất điện giữa chừng không tự thử lại cữ đó, vì có thể đã nhả một phần.
Đồng hồ chạy lùi sang ngày cũ sẽ chặn tự động cho tới khi giờ được sửa đúng.

## Dữ liệu camera cần cung cấp

Topic `petfeeder/device01/vision/pet_detected`, mỗi giây một bản tin mới, không retain:

```json
{"detected":true,"pet":"cat","confidence":0.92,"in_zone":true}
```

Khi thú rời vùng hoặc không còn nhận diện chắc chắn, gửi `detected:false`
hoặc `in_zone:false`. Receiver tự hết hạn nếu mất bản tin, và reset khi reconnect MQTT.
Confidence phải là 0–1, không phải 0–100.

## Phần chưa có trên camera thực tế

ESP32-CAM hiện **chỉ phát hiện chuyển động**, chưa có model được train.
Ngay cả model phân loại none/cat/dog trong `ml/train.py` cũng chỉ phân loại ảnh,
không tìm bounding box hay đo khoảng cách. Do đó publisher camera hiện gửi
`in_zone:false` và **không thể kích hoạt tự cho ăn**.

Để hoàn thiện cần bộ ảnh/video vị trí đặt máy và một trong hai cách:

1. Nhận diện thú cùng vùng chờ trong khung hình đã hiệu chỉnh. Vùng ảnh là điều kiện
   vị trí, không phải phép đo khoảng cách cm chính xác từ camera đơn.
2. Nhận diện thú kết hợp cảm biến khoảng cách riêng hướng ra vùng chờ.
   HC-SR04 hiện có đo thùng thức ăn, không dùng đồng thời làm cảm biến thú.

Cần điều chỉnh vùng/khoảng cách theo vị trí camera thực và kiểm thử thú đi ngang,
đứng chờ, rời vùng, quay lại sau khi ăn. Không dùng motion hoặc PIR thay cho nhận diện thú.

## Thao tác thủ công và mô phỏng

Nút trên máy và lệnh FEED của app vẫn là thao tác chủ động của người dùng,
không đòi camera. Nếu thao tác trong cửa sổ cữ chưa xử lý, máy đánh dấu cữ đó
để camera không cho ăn thêm. Những thao tác này vẫn chịu giới hạn/ngày và stale lock.

Wokwi đọc HX711 để tính thức ăn thực tế đã tăng; không tự mô phỏng hạt rơi.
Việc kéo HX711 chỉ để kiểm thử cân/motor, không phải bước của luồng tự cho ăn thực.
Wokwi hiện không có camera nhận diện thú trong `diagram.json`; kiểm thử chính sách
bằng C++ chưa thay thế kiểm thử hình ảnh/cơ khí thực tế.

Thông số `PET_WAIT_MS`, `PET_OBSERVATION_GAP_MS`, `PET_OBSERVATION_TTL_MS`,
`PET_MIN_CONFIDENCE`, `MEAL_WINDOW_MINUTES` ở `include/config.h`.
