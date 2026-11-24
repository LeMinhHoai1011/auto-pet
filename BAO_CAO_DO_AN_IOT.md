# BỘ CÔNG THƯƠNG
# TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH
# KHOA CÔNG NGHỆ THÔNG TIN
## __ o0o__

# ĐỒ ÁN HỌC PHẦN: INTERNET OF THINGS - IOT

## TÊN ĐỀ TÀI: MÁY CHO THÚ CƯNG ĂN TỰ ĐỘNG DỰA TRÊN IOT VÀ NHẬN DẠNG HÌNH ẢNH

**NHÓM: 18**

Thành phố Hồ Chí Minh, tháng 7 năm 2026

---

# ĐỀ TÀI:
# MÁY CHO THÚ CƯNG ĂN TỰ ĐỘNG DỰA TRÊN IOT VÀ NHẬN DẠNG HÌNH ẢNH

**Nhóm: 18** &emsp;&emsp; **Giảng viên hướng dẫn: Đinh Huy Hoàng**

Thành viên:

*(Điền tên thành viên nhóm 18 tại đây)*

Thành phố Hồ Chí Minh, tháng 7 năm 2026

---

# BẢNG PHÂN CÔNG CÔNG VIỆC

| Họ và tên | MSSV | Công việc | Đánh giá |
|---|---|---|---|
| *(Thành viên 1)* | *(MSSV)* | - Phụ trách viết Chương 1 và Chương 4 của báo cáo.<br>- Tổng hợp báo cáo, trình bày word.<br>- Mô phỏng Wokwi, chụp hình mô hình và bổ sung hình ảnh vào báo cáo. | 100% |
| *(Thành viên 2)* | *(MSSV)* | - Phụ trách viết Chương 2.<br>- Thiết kế PowerPoint, chuẩn bị nội dung thuyết trình.<br>- Viết kịch bản kiểm thử hệ thống. | 100% |
| *(Thành viên 3)* | *(MSSV)* | - Kết nối cảm biến HX711, DHT22, HC-SR04, Stepper Motor.<br>- Xây dựng thuật toán điều khiển nhả thức ăn và kết nối MQTT Broker.<br>- Chương 3 của báo cáo. | 100% |
| *(Thành viên 4)* | *(MSSV)* | - Phát triển chương trình ESP32 (firmware).<br>- Phát triển Web Dashboard (HTML, CSS, JavaScript).<br>- Phát triển Backend FastAPI + SQLite.<br>- Hiển thị dữ liệu thời gian thực, điều khiển thiết bị và hoàn thiện giao diện. | 100% |

---

# LỜI CAM ĐOAN

Nhóm chúng em xin cam đoan rằng báo cáo đồ án với đề tài **"Máy cho thú cưng ăn tự động dựa trên IoT và nhận dạng hình ảnh"** là kết quả nghiên cứu, tìm hiểu và thực hiện của chính nhóm dưới sự hướng dẫn của giảng viên phụ trách.

Các nội dung được trình bày trong báo cáo được xây dựng dựa trên quá trình khảo sát thực tế, nghiên cứu các tài liệu chuyên ngành, các nguồn tham khảo có uy tín và quá trình phân tích, thiết kế hệ thống của nhóm. Những thông tin, hình ảnh, bảng biểu và tài liệu tham khảo từ các nguồn khác đều được nhóm trích dẫn đầy đủ theo đúng quy định.

Nhóm xin cam kết rằng báo cáo này không sao chép nguyên văn từ bất kỳ công trình nghiên cứu hay đồ án nào đã được công bố trước đó. Mọi kết quả, nhận xét và đánh giá được trình bày trong báo cáo đều phản ánh trung thực quá trình nghiên cứu của nhóm.

Nếu có bất kỳ sai phạm nào liên quan đến bản quyền, tính trung thực trong học thuật hoặc quy định của nhà trường, nhóm xin hoàn toàn chịu trách nhiệm trước giảng viên hướng dẫn và Nhà trường.

**Nhóm thực hiện**

---

# LỜI CẢM ƠN

Trong suốt quá trình thực hiện đồ án **"Máy cho thú cưng ăn tự động dựa trên IoT và nhận dạng hình ảnh"**, nhóm đã nhận được rất nhiều sự quan tâm, hướng dẫn và hỗ trợ từ quý thầy cô, gia đình và bạn bè.

Trước hết, nhóm xin gửi lời cảm ơn chân thành đến Ban Giám hiệu cùng toàn thể quý thầy cô **Trường Đại học Công Thương Thành phố Hồ Chí Minh** đã tạo điều kiện thuận lợi về cơ sở vật chất, môi trường học tập và truyền đạt cho chúng em những kiến thức quý báu trong suốt quá trình học tập.

Đặc biệt, nhóm xin bày tỏ lòng biết ơn sâu sắc đến giảng viên hướng dẫn **Thầy Đinh Huy Hoàng** đã tận tình hướng dẫn, góp ý và hỗ trợ nhóm trong suốt quá trình nghiên cứu, phân tích yêu cầu, lựa chọn công nghệ và hoàn thiện báo cáo. Những ý kiến đóng góp của thầy đã giúp nhóm hoàn thiện đề tài cả về nội dung lẫn hình thức.

Nhóm cũng xin cảm ơn gia đình và bạn bè đã luôn động viên, tạo điều kiện thuận lợi và hỗ trợ trong quá trình học tập cũng như thực hiện đồ án.

Mặc dù đã cố gắng hoàn thành báo cáo một cách tốt nhất, tuy nhiên do thời gian thực hiện và kinh nghiệm còn hạn chế nên báo cáo khó tránh khỏi những thiếu sót. Nhóm rất mong nhận được những ý kiến đóng góp từ quý thầy cô để tiếp tục hoàn thiện và phát triển đề tài trong thời gian tới.

**Nhóm xin chân thành cảm ơn!**

---

# MỤC LỤC

- BẢNG PHÂN CÔNG CÔNG VIỆC
- LỜI CAM ĐOAN
- LỜI CẢM ƠN
- PHẦN MỞ ĐẦU
- CHƯƠNG 1. KHẢO SÁT ĐỀ TÀI VÀ CƠ SỞ LÝ THUYẾT
  - 1.1. Giới thiệu bài toán
  - 1.2. Khảo sát thực trạng và nhu cầu xây dựng hệ thống
    - 1.2.1. Thực trạng các phương pháp cho thú cưng ăn hiện nay
    - 1.2.2. So sánh các phương pháp cho ăn
    - 1.2.3. Hạn chế của phương pháp hiện tại
    - 1.2.4. Nhu cầu xây dựng hệ thống
  - 1.3. Khảo sát đối tượng và môi trường triển khai
    - 1.3.1. Khảo sát đối tượng thú cưng
    - 1.3.2. Khảo sát môi trường triển khai
    - 1.3.3. Khảo sát điều kiện triển khai hệ thống
    - 1.3.4. Khả năng mở rộng hệ thống
  - 1.4. Phân tích yêu cầu hệ thống
    - 1.4.1. Yêu cầu chức năng
    - 1.4.2. Yêu cầu phi chức năng
  - 1.5. Khảo sát và lựa chọn công nghệ
    - 1.5.1. Khảo sát và lựa chọn vi điều khiển
    - 1.5.2. Khảo sát và lựa chọn cảm biến cân nặng (Loadcell + HX711)
    - 1.5.3. Khảo sát và lựa chọn cảm biến khoảng cách (HC-SR04)
    - 1.5.4. Khảo sát và lựa chọn động cơ nhả thức ăn
    - 1.5.5. Khảo sát và lựa chọn giao thức truyền thông (MQTT)
    - 1.5.6. Web Dashboard
    - 1.5.7. Visual Studio Code và PlatformIO
    - 1.5.8. Wokwi Simulator
- CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG
  - 2.1. Phân tích yêu cầu hệ thống
  - 2.2. Kiến trúc hệ thống
  - 2.3. Phân tích các thành phần của hệ thống
  - 2.4. Thiết kế chức năng hệ thống
  - 2.5. Thiết kế giao diện Web Dashboard
  - 2.6. Thiết kế cơ sở dữ liệu
  - 2.7. Quy trình triển khai hệ thống
  - 2.8. Kịch bản kiểm thử hệ thống
- CHƯƠNG 3. XÂY DỰNG VÀ TRIỂN KHAI HỆ THỐNG
  - 3.1. Mô hình triển khai hệ thống
  - 3.2. Thiết kế và kết nối phần cứng
  - 3.3. Thiết kế giao diện giám sát người dùng (Web Dashboard)
  - 3.4. Bảng điều khiển và cấu hình hệ thống
- CHƯƠNG 4. ĐÁNH GIÁ KẾT QUẢ VÀ HƯỚNG PHÁT TRIỂN
  - 4.1. Đánh giá kết quả thực hiện
  - 4.2. Đánh giá tính khả thi
  - 4.3. Ưu điểm và hạn chế
  - 4.4. Hướng phát triển của hệ thống
- KẾT LUẬN
- LỜI KẾT THÚC
- TÀI LIỆU THAM KHẢO

---

# PHẦN MỞ ĐẦU

Trong những năm gần đây, cùng với sự phát triển mạnh mẽ của cuộc Cách mạng công nghiệp lần thứ tư (Industry 4.0), công nghệ Internet vạn vật (Internet of Things - IoT) đã trở thành một trong những nền tảng quan trọng thúc đẩy quá trình chuyển đổi số trong nhiều lĩnh vực như công nghiệp, y tế, giao thông và đặc biệt là chăm sóc thú cưng thông minh (Smart Pet Care). Việc ứng dụng IoT cho phép kết nối các thiết bị cảm biến, hệ thống điều khiển và nền tảng quản lý, góp phần tự động hóa quy trình chăm sóc thú cưng, nâng cao hiệu quả quản lý và sử dụng tối ưu các nguồn tài nguyên.

Trong lĩnh vực chăm sóc thú cưng, việc cho ăn đúng giờ và đúng liều lượng là một trong những yếu tố ảnh hưởng trực tiếp đến sức khỏe và sự phát triển của thú cưng. Tuy nhiên, tại nhiều hộ gia đình, việc cho thú cưng ăn vẫn chủ yếu được thực hiện thủ công hoặc theo thói quen của người chăm sóc. Phương pháp này khó đảm bảo chính xác thời điểm và khẩu phần ăn, dễ dẫn đến tình trạng thiếu ăn hoặc cho ăn dư thừa, gây ảnh hưởng đến sức khỏe của thú cưng. Ngoài ra, việc giám sát và quản lý việc cho ăn từ xa còn gặp nhiều khó khăn, đặc biệt khi người sử dụng phải đi công tác hoặc không thường xuyên có mặt tại nhà.

Xuất phát từ những yêu cầu thực tiễn đó, nhóm lựa chọn nghiên cứu và thực hiện đề tài **"Máy cho thú cưng ăn tự động dựa trên IoT và nhận dạng hình ảnh"**. Đề tài hướng đến việc xây dựng một hệ thống có khả năng cho thú cưng ăn theo lịch trình đã cài đặt, nhận dạng thú cưng thông qua camera, cân đo chính xác khẩu phần thức ăn bằng loadcell, giám sát mức thức ăn trong thùng chứa và điều khiển từ xa thông qua Web Dashboard. Qua đó, hệ thống góp phần nâng cao hiệu quả chăm sóc thú cưng, đảm bảo khẩu phần ăn chính xác, giảm sự phụ thuộc vào thao tác thủ công và tăng tính chủ động trong quá trình quản lý.

Bên cạnh việc xây dựng mô hình hệ thống, đề tài còn tập trung khảo sát nhu cầu của người sử dụng, phân tích các yêu cầu chức năng và phi chức năng, nghiên cứu các công nghệ phù hợp, thiết kế kiến trúc hệ thống và đánh giá khả năng vận hành thông qua các kịch bản kiểm thử. Kết quả nghiên cứu là cơ sở để xây dựng một mô hình máy cho thú cưng ăn thông minh có tính ổn định, dễ triển khai và có khả năng mở rộng trong tương lai.

Thông qua quá trình thực hiện đề tài, nhóm có cơ hội vận dụng và củng cố các kiến thức đã được học về Internet vạn vật (IoT), lập trình nhúng, mạng truyền thông, cơ sở dữ liệu và phát triển ứng dụng Web. Đồng thời, đề tài cũng góp phần minh họa khả năng ứng dụng các công nghệ hiện đại vào giải quyết những bài toán thực tiễn trong lĩnh vực chăm sóc thú cưng, tạo tiền đề cho việc nghiên cứu và phát triển các hệ thống chăm sóc thú cưng thông minh trong tương lai.

**1. Lý do chọn đề tài:**

Sự phát triển của công nghệ Internet vạn vật (IoT) đã tạo điều kiện để tự động hóa nhiều hoạt động trong đời sống hàng ngày. Trong đó, chăm sóc thú cưng là một nhu cầu ngày càng lớn khi số lượng hộ gia đình nuôi thú cưng tăng nhanh. Việc cho ăn vẫn chủ yếu được thực hiện thủ công, dẫn đến khó kiểm soát khẩu phần và thời gian cho ăn. Bên cạnh đó, nhu cầu giám sát và điều khiển từ xa ngày càng trở nên cần thiết đối với người chủ bận rộn.

Xuất phát từ thực tế đó, nhóm lựa chọn đề tài **"Máy cho thú cưng ăn tự động dựa trên IoT và nhận dạng hình ảnh"** nhằm nghiên cứu và xây dựng một giải pháp ứng dụng IoT giúp tự động hóa quá trình cho ăn, kiểm soát chính xác khẩu phần và nâng cao hiệu quả quản lý.

**2. Mục tiêu nghiên cứu:**

- Khảo sát bài toán và nhu cầu người sử dụng.
- Thiết kế và xây dựng hệ thống máy cho thú cưng ăn tự động.
- Xây dựng giao diện giám sát và điều khiển từ xa.
- Tích hợp nhận dạng hình ảnh thú cưng để tự động cho ăn.
- Kiểm thử và đánh giá hiệu quả hoạt động của hệ thống.

**3. Đối tượng và phạm vi nghiên cứu:**

*Đối tượng nghiên cứu*

Đề tài nghiên cứu hệ thống máy cho thú cưng ăn tự động ứng dụng công nghệ IoT, bao gồm các thiết bị phần cứng, phần mềm và giao thức truyền thông phục vụ việc giám sát và điều khiển quá trình cho ăn.

*Phạm vi nghiên cứu*

Đề tài triển khai mô hình máy cho thú cưng ăn cho hộ gia đình với các chức năng: cho ăn theo lịch trình, nhận dạng thú cưng, cân đo khẩu phần chính xác, giám sát mức thức ăn thùng chứa và điều khiển từ xa. Đề tài chưa triển khai trên quy mô lớn và nhận dạng hình ảnh mới ở mức demo.

**4. Phương pháp nghiên cứu:**

Đề tài được thực hiện thông qua các phương pháp: khảo sát nhu cầu thực tế, nghiên cứu tài liệu về IoT và các công nghệ liên quan, phân tích và thiết kế hệ thống, xây dựng mô hình thực nghiệm, sau đó tiến hành kiểm thử và đánh giá kết quả hoạt động của hệ thống.

---

# CHƯƠNG 1. KHẢO SÁT ĐỀ TÀI VÀ CƠ SỞ LÝ THUYẾT

## 1.1. Giới thiệu bài toán

Trong bối cảnh chuyển đổi số và sự phát triển mạnh mẽ của Internet of Things (IoT), việc ứng dụng công nghệ vào lĩnh vực chăm sóc thú cưng đang trở thành xu hướng nhằm nâng cao chất lượng cuộc sống và giảm gánh nặng cho người chủ. Đối với các hộ gia đình nuôi chó, mèo, việc cho ăn vẫn chủ yếu được thực hiện thủ công, dẫn đến khó kiểm soát khẩu phần, dễ cho ăn thừa hoặc thiếu, và gặp khó khăn khi người chủ vắng nhà.

Để khắc phục những hạn chế trên, nhóm đề xuất xây dựng **Máy cho thú cưng ăn tự động dựa trên IoT và nhận dạng hình ảnh**. Hệ thống sử dụng cảm biến loadcell (HX711) để cân đo chính xác khẩu phần thức ăn, cảm biến siêu âm HC-SR04 để theo dõi mức thức ăn trong thùng chứa, cảm biến DHT22 để giám sát nhiệt độ và độ ẩm môi trường, kết hợp ESP32 để thu thập dữ liệu và điều khiển động cơ stepper nhả thức ăn. Dữ liệu được truyền thông qua giao thức MQTT đến máy chủ FastAPI để lưu trữ, xử lý và hiển thị trên Web Dashboard. Ngoài ra, hệ thống còn tích hợp camera (ESP32-CAM) để nhận dạng thú cưng, chỉ cho ăn khi phát hiện thú cưng đến gần.

Đề tài hướng đến việc xây dựng một hệ thống có chi phí thấp, dễ triển khai, dễ mở rộng và phù hợp với các hộ gia đình nuôi thú cưng.

## 1.2. Khảo sát thực trạng và nhu cầu xây dựng hệ thống

### 1.2.1. Thực trạng các phương pháp cho thú cưng ăn hiện nay

Hiện nay việc cho thú cưng ăn chủ yếu được thực hiện bằng phương pháp thủ công. Người sử dụng tự quan sát và quyết định thời điểm cũng như lượng thức ăn cần cho.

Hiện nay, việc cho thú cưng ăn phổ biến được thực hiện bằng các phương pháp sau:

**a. Cho ăn thủ công**

Người sử dụng trực tiếp đổ thức ăn vào bát dựa trên kinh nghiệm và quan sát thực tế.

Ưu điểm:
- Chi phí thấp.
- Dễ thực hiện.
- Không yêu cầu thiết bị hỗ trợ.

Nhược điểm:
- Phụ thuộc vào con người.
- Khó kiểm soát khẩu phần chính xác.
- Không phù hợp khi người chủ đi vắng.
- Dễ quên cho ăn hoặc cho ăn không đúng giờ.

**b. Máy cho ăn tự động theo hẹn giờ**

Hệ thống sử dụng bộ hẹn giờ để mở nắp thùng chứa thức ăn theo lịch đã thiết lập.

Ưu điểm:
- Giảm công sức chăm sóc.
- Có thể tự động cho ăn theo lịch.

Nhược điểm:
- Không cân đo chính xác khẩu phần.
- Có thể cho ăn khi bát còn thức ăn cũ.
- Không giám sát được từ xa.
- Không phát hiện thức ăn thiu hoặc sự cố.

**c. Máy cho ăn thông minh sử dụng IoT**

Hệ thống sử dụng cảm biến, bộ điều khiển và Internet để tự động giám sát và điều khiển quá trình cho ăn.

Ưu điểm:
- Cho ăn dựa trên dữ liệu cân nặng thực tế.
- Kiểm soát khẩu phần chính xác.
- Theo dõi dữ liệu theo thời gian thực.
- Điều khiển từ xa.
- Có khả năng nhận dạng thú cưng.
- Có khả năng mở rộng.

### 1.2.2. So sánh các phương pháp cho ăn

| Tiêu chí | Thủ công | Hẹn giờ | IoT thông minh |
|---|---|---|---|
| Mức độ tự động | Thấp | Trung bình | Cao |
| Cân đo khẩu phần | Không | Không chính xác | Chính xác |
| Nhận dạng thú cưng | Không | Không | Có |
| Điều khiển từ xa | Không | Không | Có |
| Giám sát mức thức ăn | Không | Không | Có |
| Phát hiện sự cố | Không | Không | Có |
| Khả năng mở rộng | Thấp | Trung bình | Cao |

### 1.2.3. Hạn chế của phương pháp hiện tại

Qua khảo sát, các phương pháp cho thú cưng ăn truyền thống còn tồn tại một số hạn chế:

- Người dùng dễ quên cho ăn khi bận hoặc đi xa.
- Không xác định chính xác khẩu phần cần thiết.
- Có thể gây thừa ăn hoặc thiếu ăn, ảnh hưởng sức khỏe thú cưng.
- Không theo dõi được tình trạng thức ăn từ xa.
- Không phát hiện thức ăn bị thiu hoặc hỏng.
- Không có khả năng nhận dạng thú cưng để cho ăn đúng đối tượng.

Do đó, việc xây dựng một hệ thống cho ăn thông minh ứng dụng IoT là cần thiết nhằm giải quyết các hạn chế trên.

### 1.2.4. Nhu cầu xây dựng hệ thống

Dựa trên thực trạng khảo sát, hệ thống cần đáp ứng các yêu cầu:

| Chức năng | Mục đích |
|---|---|
| Cho ăn theo lịch trình | Đảm bảo thú cưng được ăn đúng giờ |
| Cân đo khẩu phần | Kiểm soát lượng thức ăn chính xác |
| Nhận dạng thú cưng | Cho ăn khi thú cưng có mặt |
| Giám sát mức thức ăn | Phát hiện sắp hết thức ăn trong thùng |
| Điều khiển từ xa | Quản lý hệ thống qua Internet |
| Theo dõi lịch sử | Đánh giá quá trình cho ăn |
| Cảnh báo sự cố | Phát hiện kẹt thức ăn, thức ăn thiu |
| Giám sát môi trường | Theo dõi nhiệt độ, độ ẩm bảo quản thức ăn |

## 1.3. Khảo sát đối tượng và môi trường triển khai

### 1.3.1. Khảo sát đối tượng thú cưng

Việc xác định đối tượng thú cưng là yếu tố quan trọng trong hệ thống cho ăn thông minh vì mỗi loại thú cưng có nhu cầu ăn và khẩu phần khác nhau. Dựa vào cân nặng và tần suất ăn, hệ thống có thể đưa ra khẩu phần phù hợp.

Trong phạm vi đề tài, nhóm hướng đến các loại thú cưng phổ biến trong hộ gia đình như chó nhỏ, mèo.

**Bảng 1.1. Nhu cầu ăn của một số nhóm thú cưng**

| Loại thú cưng | Đặc điểm | Khẩu phần/bữa | Số bữa/ngày |
|---|---|---|---|
| Mèo | Ăn ít nhiều lần, thích ăn theo nhu cầu | 20–40g | 3–4 |
| Chó nhỏ (<10kg) | Ăn theo bữa, năng lượng cao | 30–60g | 2–3 |
| Chó trung bình (10–25kg) | Khẩu phần lớn hơn, ăn đều đặn | 60–120g | 2 |

Dựa trên bảng khảo sát, hệ thống cho phép người dùng thiết lập khẩu phần và lịch ăn phù hợp với từng loại thú cưng. Tối đa 6 cữ ăn/ngày, mỗi cữ từ 10–150g, giới hạn tổng 150g/ngày.

### 1.3.2. Khảo sát môi trường triển khai

Hệ thống máy cho thú cưng ăn có thể triển khai trong nhiều môi trường khác nhau. Tuy nhiên, trong phạm vi đồ án, nhóm tập trung xây dựng mô hình phù hợp với hộ gia đình.

**a. Trong nhà**

Ví dụ:
- Phòng khách.
- Nhà bếp.
- Ban công.

Đặc điểm:
- Có nguồn điện ổn định.
- Có kết nối Wi-Fi.
- Ít chịu ảnh hưởng của thời tiết.

Yêu cầu:
- Thiết bị nhỏ gọn.
- Hoạt động êm ái.
- Dễ vệ sinh.

**b. Ngoài trời (có mái che)**

Ví dụ:
- Sân vườn có mái.
- Hiên nhà.

Đặc điểm:
- Chịu ảnh hưởng bởi nhiệt độ, độ ẩm.
- Thức ăn dễ bị ẩm mốc.

Yêu cầu:
- Hộp bảo vệ thiết bị.
- Cảm biến giám sát nhiệt độ, độ ẩm.
- Phát hiện thức ăn thiu.

Trong phạm vi đề tài, nhóm lựa chọn môi trường triển khai là hộ gia đình trong nhà. Đây là môi trường phù hợp với khả năng của hệ thống sử dụng ESP32, Wi-Fi và các cảm biến phổ biến.

### 1.3.3. Khảo sát điều kiện triển khai hệ thống

Để hệ thống hoạt động ổn định, cần đảm bảo các điều kiện về kết nối, nguồn điện và thiết bị.

**a. Kết nối Internet**

ESP32 sử dụng Wi-Fi để truyền dữ liệu lên máy chủ thông qua giao thức MQTT.

Yêu cầu:
- Kết nối Wi-Fi ổn định.
- Đảm bảo truyền dữ liệu liên tục.
- Hỗ trợ điều khiển từ xa.

Nếu mất kết nối:
- Hệ thống vẫn hoạt động offline (offline-first).
- Lịch ăn được lưu trong bộ nhớ NVS của ESP32.
- Sự kiện được lưu tạm trong hàng đợi LittleFS, gửi lên khi có mạng.

**b. Nguồn điện**

Hệ thống sử dụng các nguồn điện khác nhau:

| Thiết bị | Điện áp |
|---|---|
| ESP32 | 3.3V – 5V |
| Stepper Motor + A4988 | 12V |
| HX711 Loadcell | 3.3V – 5V |
| HC-SR04 | 5V |
| DHT22 | 3.3V – 5V |
| OLED SSD1306 | 3.3V |

Nguồn điện cần đảm bảo ổn định để hệ thống hoạt động liên tục.

**c. Thức ăn**

Hệ thống cần đảm bảo:
- Sử dụng thức ăn hạt khô cho chó/mèo.
- Thùng chứa có dung tích phù hợp.
- Cơ cấu nhả thức ăn không bị kẹt.

### 1.3.4. Khả năng mở rộng hệ thống

Một ưu điểm của hệ thống IoT là khả năng mở rộng khi nhu cầu sử dụng tăng lên.

Trong tương lai, hệ thống có thể được mở rộng:

**Mở rộng số lượng thiết bị:**
- Thêm nhiều máy cho ăn cho nhiều thú cưng.
- Quản lý tập trung trên một Dashboard.

**Tích hợp thêm cảm biến:**
- Camera AI nhận dạng từng thú cưng riêng biệt.
- Cảm biến cân nặng thú cưng.
- Cảm biến mực nước bình uống.

**Phát triển ứng dụng quản lý:**
- Ứng dụng Android/iOS (Flutter).
- Thông báo đẩy qua điện thoại.
- Điều khiển bằng giọng nói.

## 1.4. Phân tích yêu cầu hệ thống

Sau quá trình khảo sát thực trạng và nhu cầu người dùng, hệ thống máy cho thú cưng ăn tự động cần đáp ứng các yêu cầu chức năng và phi chức năng nhằm đảm bảo khả năng hoạt động hiệu quả.

### 1.4.1. Yêu cầu chức năng

**a. Thu thập dữ liệu cảm biến**

Hệ thống có khả năng:
- Đọc giá trị cân nặng thức ăn trong bát (HX711 Loadcell).
- Đo khoảng cách mức thức ăn trong thùng chứa (HC-SR04).
- Thu thập nhiệt độ và độ ẩm môi trường (DHT22).
- Thu thập dữ liệu định kỳ.
- Gửi dữ liệu lên máy chủ qua MQTT.

**b. Cho ăn tự động theo lịch trình**

Hệ thống thực hiện:
- Cho ăn theo lịch trình đã cài đặt (tối đa 6 cữ/ngày).
- Cân đo chính xác khẩu phần bằng loadcell.
- Bỏ qua cữ ăn nếu bát còn ≥50% thức ăn.
- Chỉ nhả phần còn thiếu = khẩu phần − lượng đang có.

**c. Cho ăn khi nhận dạng thú cưng**

Hệ thống thực hiện:
- Nhận dạng thú cưng qua camera (ESP32-CAM).
- Chỉ cho ăn khi phát hiện thú cưng hiện diện ≥5 giây.
- Áp dụng cooldown 2 tiếng giữa các lần cho ăn.
- Không cho ăn trong khung giờ 23:00–05:00.

**d. Điều khiển thủ công**

Người dùng có thể:
- Nhấn nút cho ăn trên thiết bị.
- Cho ăn từ xa qua Web Dashboard.
- Chế độ cho ăn thủ công bỏ qua cooldown nhưng tôn trọng giới hạn ngày.

**e. Giám sát hệ thống**

Web Dashboard cho phép người dùng:
- Xem cân nặng thức ăn trong bát.
- Xem mức thức ăn thùng chứa.
- Xem nhiệt độ và độ ẩm.
- Xem trạng thái kết nối thiết bị.
- Theo dõi lịch sử cho ăn.
- Xem danh sách cảnh báo.

**f. Cảnh báo sự cố**

Hệ thống cảnh báo khi:
- Thùng chứa sắp hết thức ăn (<20%).
- Độ ẩm môi trường cao (>70%).
- Kẹt thức ăn (motor chạy, loadcell không tăng).
- Thú cưng bỏ bữa (nhả >4 tiếng mà cân không giảm).
- Thức ăn có dấu hiệu thiu.
- Chống spam cảnh báo: 1 lần / 6 tiếng mỗi loại.

**g. Lưu trữ dữ liệu**

Hệ thống lưu:
- Lịch sử cho ăn (nguồn, khẩu phần, kết quả).
- Giá trị cảm biến.
- Danh sách cảnh báo.
- Lịch ăn đã cấu hình.
- Trạng thái thiết bị.

### 1.4.2. Yêu cầu phi chức năng

Ngoài các chức năng chính, hệ thống cần đảm bảo các yêu cầu:

| Yêu cầu | Mô tả |
|---|---|
| Hiệu năng | Cập nhật dữ liệu gần thời gian thực qua WebSocket |
| Ổn định | Hoạt động liên tục, offline-first |
| Dễ sử dụng | Giao diện trực quan, hỗ trợ dark/light theme |
| Khả năng mở rộng | Có thể thêm thiết bị và cảm biến |
| Chi phí thấp | Phù hợp hộ gia đình |
| An toàn thực phẩm | Phát hiện thức ăn thiu, giám sát nhiệt độ/độ ẩm |

## 1.5. Khảo sát và lựa chọn công nghệ

Sau khi khảo sát các giải pháp hiện có, nhóm tiến hành lựa chọn những công nghệ phù hợp với phạm vi và mục tiêu của đề tài. Tiêu chí lựa chọn bao gồm tính ổn định, dễ triển khai, chi phí thấp, khả năng mở rộng và phù hợp với môi trường học tập, nghiên cứu.

Hệ thống sử dụng các công nghệ chính gồm: **ESP32**, **Loadcell HX711**, **HC-SR04**, **DHT22**, **Stepper Motor A4988**, **MQTT Broker (Mosquitto)**, **FastAPI + SQLite**, **Web Dashboard** và **Wokwi Simulator**.

### 1.5.1. Khảo sát và lựa chọn vi điều khiển

**a. Giới thiệu ESP32**

ESP32 là một dòng vi điều khiển được phát triển bởi Espressif Systems, được sử dụng phổ biến trong các ứng dụng IoT nhờ khả năng tích hợp Wi-Fi, Bluetooth và hiệu năng xử lý tốt.

Trong hệ thống máy cho thú cưng ăn, ESP32 đóng vai trò là bộ điều khiển trung tâm, thực hiện các nhiệm vụ:
- Thu thập dữ liệu từ các cảm biến (HX711, HC-SR04, DHT22).
- Xử lý dữ liệu cảm biến và so sánh với ngưỡng.
- Kết nối Wi-Fi.
- Gửi/nhận dữ liệu thông qua MQTT.
- Điều khiển Stepper Motor nhả thức ăn.
- Hiển thị thông tin trên OLED.
- Lưu trữ cấu hình và hàng đợi sự kiện (NVS + LittleFS).

**b. So sánh một số vi điều khiển**

| Tiêu chí | Arduino Uno | ESP8266 | ESP32 |
|---|---|---|---|
| Wi-Fi tích hợp | Không | Có | Có |
| Bluetooth | Không | Không | Có |
| Hiệu năng xử lý | Trung bình | Khá | Cao |
| Số chân GPIO | Ít | Trung bình | Nhiều |
| ADC | 1 kênh | 1 kênh | Nhiều kênh |
| Phù hợp IoT | Trung bình | Tốt | Rất tốt |

**c. Lý do lựa chọn ESP32**

Nhóm lựa chọn ESP32 vì:
- Có sẵn kết nối Wi-Fi.
- Hiệu năng cao, hỗ trợ đa luồng.
- Giá thành phù hợp.
- Hỗ trợ nhiều thư viện IoT (PubSubClient, ArduinoJson, AccelStepper...).
- Nhiều chân GPIO, đủ kết nối tất cả cảm biến và module.
- Hỗ trợ NVS và LittleFS để lưu trữ offline.
- Phù hợp với các hệ thống giám sát và điều khiển từ xa.

### 1.5.2. Khảo sát và lựa chọn cảm biến cân nặng (Loadcell + HX711)

**a. Giới thiệu**

Loadcell là cảm biến lực, kết hợp với module khuếch đại HX711, dùng để đo chính xác trọng lượng thức ăn trong bát. Đây là thành phần cốt lõi giúp hệ thống nhả thức ăn theo gram chính xác.

**b. Nguyên lý hoạt động**

- Loadcell biến dạng khi có lực tác dụng → thay đổi điện trở → tạo tín hiệu điện nhỏ.
- HX711 khuếch đại tín hiệu và chuyển đổi sang dạng số 24-bit.
- ESP32 đọc giá trị từ HX711, nhân với hệ số hiệu chỉnh để tính gram.

**c. Lý do lựa chọn**

Nhóm lựa chọn Loadcell + HX711 vì:
- Độ chính xác cao (±0.5g).
- Giá thành thấp.
- Dễ kết nối với ESP32 qua 2 chân (DT, SCK).
- Hỗ trợ auto-tare (tự động trừ bì).
- Phù hợp cho ứng dụng cân thức ăn.

### 1.5.3. Khảo sát và lựa chọn cảm biến khoảng cách (HC-SR04)

**a. Giới thiệu**

HC-SR04 là cảm biến siêu âm dùng để đo khoảng cách. Trong hệ thống, HC-SR04 được gắn trên nắp thùng chứa thức ăn, hướng xuống để đo mức thức ăn còn lại.

**b. Nguyên lý hoạt động**

- Phát sóng siêu âm từ chân TRIG.
- Nhận tín hiệu phản hồi từ chân ECHO.
- Tính khoảng cách = (thời gian x vận tốc âm thanh) / 2.
- Quy đổi khoảng cách → phần trăm mức thức ăn.

**c. Lý do lựa chọn**

Nhóm lựa chọn HC-SR04 vì:
- Chi phí thấp.
- Dễ sử dụng.
- Phạm vi đo phù hợp (2–400cm).
- Đủ chính xác cho mục đích giám sát mức thức ăn.

### 1.5.4. Khảo sát và lựa chọn động cơ nhả thức ăn

**a. Giới thiệu**

Stepper Motor (động cơ bước) kết hợp với driver A4988 được sử dụng để điều khiển cơ cấu nhả thức ăn. Stepper motor quay từng bước chính xác, phù hợp cho việc nhả thức ăn theo từng đợt nhỏ.

**b. So sánh Servo và Stepper Motor**

| Tiêu chí | Servo MG996R | Stepper Motor + A4988 |
|---|---|---|
| Độ chính xác | Trung bình | Cao |
| Mô-men xoắn | Trung bình | Cao |
| Điều khiển | Góc quay | Số bước |
| Nhả theo đợt | Khó kiểm soát | Chính xác |
| Encoder phản hồi | Không | Có thể tích hợp |

**c. Lý do lựa chọn Stepper Motor**

Nhóm lựa chọn Stepper Motor + A4988 vì:
- Điều khiển chính xác số bước quay.
- Phù hợp cho cơ cấu vít xoắn nhả thức ăn.
- Có thể đảo chiều khi phát hiện kẹt.
- Tích hợp encoder để xác nhận trục đã quay.
- Mô-men xoắn đủ lớn cho thức ăn hạt khô.

### 1.5.5. Khảo sát và lựa chọn giao thức truyền thông (MQTT)

**a. Giới thiệu**

MQTT (Message Queuing Telemetry Transport) là giao thức nhắn tin nhẹ, thiết kế cho các thiết bị IoT có tài nguyên hạn chế. MQTT hoạt động theo mô hình Publish/Subscribe thông qua một Broker trung gian.

**b. So sánh các giao thức**

| Tiêu chí | HTTP | MQTT | WebSocket |
|---|---|---|---|
| Mô hình | Request/Response | Publish/Subscribe | Full-duplex |
| Tiêu tốn tài nguyên | Cao | Thấp | Trung bình |
| Phù hợp IoT | Trung bình | Rất tốt | Tốt |
| Hỗ trợ QoS | Không | Có (0, 1, 2) | Không |

**c. Lý do lựa chọn MQTT**

Nhóm lựa chọn MQTT vì:
- Nhẹ, phù hợp ESP32 với tài nguyên hạn chế.
- Hỗ trợ QoS đảm bảo tin nhắn được gửi.
- Dễ tích hợp với ESP32 (PubSubClient) và Python (aiomqtt).
- Hỗ trợ Last Will để phát hiện thiết bị mất kết nối.
- Broker Mosquitto miễn phí, ổn định.

### 1.5.6. Web Dashboard

**a. Giới thiệu**

Web Dashboard là giao diện giúp người dùng theo dõi và điều khiển hệ thống thông qua trình duyệt web. Đây là nơi hiển thị toàn bộ dữ liệu được thu thập từ ESP32 và cho phép người dùng tương tác với hệ thống từ xa.

**b. Chức năng chính**

Dashboard được xây dựng nhằm cung cấp các chức năng:
- Hiển thị cân nặng thức ăn trong bát theo thời gian thực.
- Hiển thị mức thức ăn thùng chứa (%).
- Hiển thị nhiệt độ và độ ẩm môi trường.
- Hiển thị trạng thái kết nối thiết bị (online/offline).
- Nút cho ăn từ xa (Feed Now).
- Quản lý lịch ăn (thêm, sửa, xóa cữ ăn).
- Xem lịch sử cho ăn.
- Xem danh sách cảnh báo.
- Hỗ trợ Dark/Light theme.
- Biểu đồ theo dõi dữ liệu cảm biến.

**c. Công nghệ sử dụng**

- **Backend**: FastAPI (Python) + SQLite + aiomqtt.
- **Frontend**: HTML, CSS, JavaScript thuần.
- **Real-time**: WebSocket để cập nhật dữ liệu tức thì.
- **API**: RESTful API cho các thao tác CRUD.

**d. Lý do lựa chọn**

Nhóm lựa chọn Web Dashboard vì:
- Phù hợp với các hệ thống IoT.
- Chi phí triển khai thấp.
- Truy cập được trên mọi thiết bị có trình duyệt.
- Thuận tiện cho việc giám sát và điều khiển từ xa.

### 1.5.7. Visual Studio Code và PlatformIO

**a. Giới thiệu**

Visual Studio Code (VS Code) là môi trường phát triển mã nguồn (IDE) miễn phí do Microsoft phát triển. PlatformIO là extension cho VS Code, hỗ trợ phát triển firmware cho các vi điều khiển bao gồm ESP32.

**b. Vai trò trong hệ thống**

VS Code + PlatformIO được sử dụng để:
- Viết chương trình firmware ESP32 (C/C++).
- Quản lý thư viện (HX711, AccelStepper, PubSubClient...).
- Build và upload firmware.
- Phát triển Backend FastAPI (Python).
- Phát triển giao diện Web Dashboard.
- Quản lý toàn bộ mã nguồn.

**c. Lý do lựa chọn**

Nhóm lựa chọn VS Code + PlatformIO vì:
- Miễn phí, nhẹ và dễ sử dụng.
- PlatformIO hỗ trợ tốt cho ESP32.
- Tích hợp Wokwi Simulator để mô phỏng.
- Quản lý dependencies tự động.

### 1.5.8. Wokwi Simulator

**a. Giới thiệu**

Wokwi Simulator là nền tảng mô phỏng phần cứng trực tuyến, cho phép kiểm thử các chương trình nhúng mà không cần sử dụng thiết bị thật.

**b. Vai trò trong hệ thống**

Wokwi giúp nhóm:
- Mô phỏng ESP32.
- Mô phỏng Stepper Motor + A4988.
- Mô phỏng HX711 Loadcell.
- Mô phỏng HC-SR04.
- Mô phỏng DHT22.
- Mô phỏng OLED SSD1306, RTC DS1307.
- Mô phỏng nút nhấn, buzzer, LED.
- Kết nối MQTT qua host.wokwi.internal.

**c. Lý do lựa chọn**

Nhóm lựa chọn Wokwi Simulator vì:
- Phù hợp với quá trình học tập và nghiên cứu.
- Hỗ trợ tốt cho ESP32.
- Tích hợp trực tiếp với VS Code + PlatformIO.
- Tiết kiệm chi phí phát triển.
- Hỗ trợ nhiều linh kiện IoT.

---

# CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

## 2.1. Phân tích yêu cầu hệ thống

### 2.1.1. Mục tiêu hệ thống

Mục tiêu của hệ thống là xây dựng một mô hình máy cho thú cưng ăn tự động có khả năng cho ăn theo lịch trình, nhận dạng thú cưng, cân đo chính xác khẩu phần thức ăn, giám sát mức thức ăn thùng chứa và điều khiển từ xa, góp phần nâng cao hiệu quả chăm sóc thú cưng và giảm sự phụ thuộc vào người chăm sóc.

Hệ thống cho phép người dùng theo dõi trạng thái thiết bị thông qua Web Dashboard, điều khiển cho ăn từ xa hoặc vận hành tự động theo lịch trình và dữ liệu từ camera.

### 2.1.2. Yêu cầu chức năng của hệ thống

**Bảng 2.1. Yêu cầu chức năng của hệ thống**

| STT | Chức năng | Mô tả |
|---|---|---|
| 1 | Đọc dữ liệu cảm biến | Thu thập cân nặng bát, mức thùng chứa, nhiệt độ, độ ẩm từ ESP32 |
| 2 | Hiển thị dữ liệu | Hiển thị dữ liệu thời gian thực trên Web Dashboard qua WebSocket |
| 3 | Cho ăn theo lịch | Tự động nhả thức ăn theo lịch trình đã cài đặt |
| 4 | Cho ăn khi nhận dạng | Nhả thức ăn khi camera phát hiện thú cưng |
| 5 | Cho ăn thủ công | Cho phép bật cho ăn từ nút hoặc Dashboard |
| 6 | Cân đo khẩu phần | Nhả thức ăn từng đợt, dừng khi đạt đủ gram mục tiêu |
| 7 | Cấu hình lịch ăn | Thêm, sửa, xóa cữ ăn (tối đa 6 cữ/ngày) |
| 8 | Giám sát trạng thái | Hiển thị trạng thái kết nối, mức thùng, nhiệt độ, độ ẩm |
| 9 | Cảnh báo sự cố | Phát hiện kẹt, thức ăn thiu, thùng sắp hết, độ ẩm cao |
| 10 | Lưu trữ lịch sử | Ghi log cho ăn, cảm biến, cảnh báo vào SQLite |

### 2.1.3. Yêu cầu phi chức năng

Ngoài các yêu cầu về chức năng, hệ thống cần đảm bảo các yêu cầu về chất lượng.

**Bảng 2.2. Yêu cầu phi chức năng**

| Tiêu chí | Yêu cầu |
|---|---|
| Hiệu năng | Dữ liệu cập nhật gần thời gian thực qua WebSocket |
| Tính ổn định | Hoạt động liên tục, offline-first (không phụ thuộc mạng) |
| Khả năng mở rộng | Có thể bổ sung thêm cảm biến và thiết bị |
| Giao diện | Đơn giản, trực quan, hỗ trợ dark/light theme |
| Bảo trì | Dễ thay đổi cấu hình và cập nhật firmware |
| Tương thích | Hoạt động trên trình duyệt máy tính và điện thoại |

## 2.2. Kiến trúc hệ thống

Hệ thống được thiết kế theo mô hình kiến trúc IoT gồm bốn tầng:

1. **Tầng Edge (Thiết bị biên)**: ESP32 + các cảm biến + Stepper Motor
2. **Tầng Gateway/Network**: WiFi + MQTT Protocol
3. **Tầng Server/Application**: FastAPI Backend + MQTT Subscriber + SQLite
4. **Tầng Presentation**: Web Dashboard + WebSocket real-time

Quá trình hoạt động được thực hiện như sau:

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

- ESP32 thu thập dữ liệu từ các cảm biến.
- Dữ liệu được gửi đến MQTT Broker (Mosquitto) thông qua Wi-Fi.
- FastAPI Backend lắng nghe các MQTT topics, xử lý và lưu vào SQLite.
- Dashboard nhận dữ liệu real-time qua WebSocket.
- Người dùng có thể cho ăn từ xa hoặc cấu hình lịch ăn trên Dashboard.
- Lệnh từ Dashboard → FastAPI → MQTT → ESP32.

## 2.3. Phân tích các thành phần của hệ thống

Hệ thống được chia thành năm khối chức năng chính.

**a. Khối thu thập dữ liệu**

Khối này bao gồm ESP32, loadcell HX711, HC-SR04 và DHT22. Nhiệm vụ của khối là đọc các thông số (cân nặng bát, mức thùng, nhiệt độ, độ ẩm) và gửi dữ liệu đến server qua MQTT.

**b. Khối xử lý và điều khiển**

ESP32 đóng vai trò trung tâm điều khiển.

Sau khi nhận dữ liệu từ cảm biến, ESP32 sẽ:
- Xử lý giá trị đọc được (lọc nhiễu loadcell, median filter);
- So sánh với ngưỡng cài đặt;
- Điều khiển stepper motor nhả thức ăn theo từng đợt;
- Phát hiện kẹt thức ăn (jam detection) thông qua encoder và loadcell;
- Quản lý lịch ăn, cooldown, giới hạn ngày.

**c. Khối nhả thức ăn**

Stepper motor quay từng đợt (200 bước/đợt), sau mỗi đợt:
- Đọc loadcell để kiểm tra lượng đã nhả;
- Nếu chưa đủ → tiếp tục nhả;
- Nếu loadcell không tăng qua 3 đợt → phát hiện kẹt → đảo chiều thử;
- Nếu vẫn kẹt → dừng và gửi cảnh báo "jam".

**d. Khối giao diện người dùng**

Web Dashboard cho phép người dùng:
- Theo dõi cân nặng bát, mức thùng, nhiệt độ, độ ẩm;
- Cho ăn từ xa (Feed Now);
- Quản lý lịch ăn;
- Xem lịch sử cho ăn và cảnh báo;
- Xem biểu đồ dữ liệu cảm biến.

**e. Khối nhận dạng thú cưng**

ESP32-CAM chụp ảnh, gửi qua MQTT topic `vision/pet_detected`:
- Cần phát hiện thú cưng qua N khung hình liên tiếp (xác nhận);
- Thú cưng hiện diện ≥5 giây → trigger cho ăn;
- Kết hợp với cooldown 2 tiếng và giới hạn ngày.

## 2.4. Thiết kế chức năng hệ thống

Hệ thống được xây dựng với nhiều chế độ hoạt động.

**a. Cho ăn theo lịch trình (Schedule)**

Quy trình hoạt động:
1. Kiểm tra thời gian hiện tại với các cữ ăn đã cài đặt.
2. Nếu đến giờ, kiểm tra bát còn thức ăn không.
3. Nếu bát còn ≥50% → bỏ qua cữ ăn, log "skipped".
4. Nếu bát gần trống → tính phần cần nhả = khẩu phần − lượng đang có.
5. Điều khiển stepper nhả từng đợt, cân đo sau mỗi đợt.
6. Dừng khi đạt đủ gram hoặc hết timeout.

**b. Cho ăn khi nhận dạng thú cưng (Camera/Vision)**

Quy trình hoạt động:
1. Camera phát hiện thú cưng → gửi MQTT `vision/pet_detected`.
2. ESP32 xác nhận: thú cưng hiện diện ≥5 giây, qua cooldown, bát gần trống, không trong 23:00–05:00.
3. Nhả khẩu phần mặc định (30g).

**c. Cho ăn thủ công (Manual/Remote)**

- Nút trên thiết bị: nhả 1 khẩu phần, bỏ qua cooldown.
- Lệnh từ Dashboard: gửi MQTT command `{"command":"FEED","amount":X}`.
- Vẫn tôn trọng giới hạn ngày (6 lần, 150g).

## 2.5. Thiết kế giao diện Web Dashboard

Web Dashboard được xây dựng dưới dạng Web nhằm hỗ trợ người dùng giám sát hệ thống theo thời gian thực và điều khiển từ xa.

Giao diện gồm các thành phần:

- **Header**: Tên hệ thống, trạng thái kết nối (online/offline), thời gian cập nhật cuối.
- **Tiles dữ liệu cảm biến**: Cân nặng bát (g), mức thùng (%), nhiệt độ (°C), độ ẩm (%).
- **Nút Feed Now**: Cho ăn từ xa với khẩu phần tùy chỉnh.
- **Lịch ăn**: Bảng các cữ ăn, có thể thêm/sửa/xóa.
- **Biểu đồ**: Đồ thị cân nặng bát theo thời gian.
- **Lịch sử cho ăn**: 20 sự kiện gần nhất.
- **Danh sách cảnh báo**: Các cảnh báo chưa xử lý.

## 2.6. Thiết kế cơ sở dữ liệu

Hệ thống sử dụng SQLite để lưu trữ dữ liệu.

**Bảng 2.3. Schema cơ sở dữ liệu**

| Bảng | Các cột chính | Mục đích |
|---|---|---|
| feeding_logs | id, device_id, source, result, target_grams, actual_grams, created_at | Lịch sử cho ăn |
| sensor_logs | id, device_id, sensor_type, value, unit, created_at | Dữ liệu cảm biến |
| alert_logs | id, device_id, alert_type, message, resolved, created_at | Danh sách cảnh báo |
| schedules | id, device_id, hour, minute, grams, enabled, created_at | Lịch ăn |
| device_states | id, device_id, bowl_grams, hopper_pct, temperature, humidity, wifi_ok, mqtt_ok, stale_score, online, updated_at | Trạng thái thiết bị |
| fcm_tokens | id, token, device_name, created_at | Token push notification |

## 2.7. Quy trình triển khai hệ thống

Sau khi hoàn thành quá trình phân tích và thiết kế, nhóm tiến hành xây dựng hệ thống theo các bước triển khai sau:

**Bước 1. Thiết kế mô hình mô phỏng trên Wokwi**

Nhóm sử dụng nền tảng Wokwi để mô phỏng hệ thống phần cứng gồm ESP32, Stepper Motor A4988, HX711 Loadcell, HC-SR04, DHT22, OLED SSD1306, RTC DS1307, nút nhấn, buzzer và LED. Việc mô phỏng giúp kiểm tra sơ đồ kết nối và nguyên lý hoạt động trước khi triển khai trên phần cứng thực tế.

**Bước 2. Lập trình vi điều khiển ESP32**

ESP32 được lập trình bằng Visual Studio Code kết hợp PlatformIO. Firmware bao gồm các module: feeder (nhả thức ăn), sensors (đọc cảm biến), schedule (lịch ăn), storage (NVS + LittleFS), display (OLED), notify (MQTT), timekeeper (NTP + RTC).

**Bước 3. Thiết lập MQTT Broker**

Hệ thống sử dụng Mosquitto MQTT Broker chạy local trên Windows. ESP32 kết nối qua `host.wokwi.internal:1883` (khi mô phỏng Wokwi).

**Bước 4. Phát triển Backend FastAPI**

Backend được phát triển bằng Python FastAPI, lắng nghe các MQTT topics, xử lý dữ liệu và lưu vào SQLite. Cung cấp REST API cho Dashboard.

**Bước 5. Xây dựng Web Dashboard**

Web Dashboard hiển thị dữ liệu cảm biến, trạng thái thiết bị, lịch sử cho ăn và cho phép điều khiển từ xa. Dữ liệu real-time qua WebSocket.

**Bước 6. Kiểm thử hệ thống**

Sau khi hoàn thành việc tích hợp, nhóm tiến hành kiểm thử toàn bộ chức năng nhằm đánh giá khả năng hoạt động, độ ổn định và tính chính xác của mô hình.

## 2.8. Kịch bản kiểm thử hệ thống

Để đánh giá khả năng hoạt động của hệ thống, nhóm xây dựng các kịch bản kiểm thử dựa trên các chức năng chính.

### 2.8.1. Kiểm thử cho ăn thành công

**Mục đích:** Kiểm tra khả năng nhả thức ăn đúng khẩu phần.

**Thực hiện:**
- Cài đặt lịch ăn hoặc gửi lệnh cho ăn 30g.
- Quan sát stepper motor quay và loadcell tăng dần.
- Kiểm tra giá trị hiển thị trên Dashboard.

**Kết quả mong đợi:** Motor nhả thức ăn từng đợt, dừng khi loadcell đạt ~30g. Dashboard hiển thị sự kiện "fed" với actual_grams ≈ target_grams.

### 2.8.2. Kiểm thử phát hiện kẹt thức ăn (Jam Detection)

**Mục đích:** Đánh giá khả năng phát hiện kẹt khi motor quay nhưng loadcell không tăng.

**Thực hiện:**
- Gửi lệnh cho ăn.
- Giữ loadcell không thay đổi (mô phỏng kẹt trên Wokwi).

**Kết quả mong đợi:** Sau 3 đợt nhả liên tiếp không tăng gram → đảo chiều thử → vẫn không tăng → dừng motor, gửi cảnh báo "jam", buzzer kêu.

### 2.8.3. Kiểm thử bỏ qua cữ ăn (Bowl Not Empty)

**Mục đích:** Kiểm tra logic bỏ qua khi bát còn nhiều thức ăn.

**Thực hiện:**
- Đặt loadcell ở giá trị cao (>15g khi khẩu phần 30g, tức >50%).
- Chờ đến giờ ăn theo lịch.

**Kết quả mong đợi:** Hệ thống log "skipped" và không nhả thức ăn. OLED hiển thị "Bo qua (bat con du)".

### 2.8.4. Kiểm thử cảnh báo thùng sắp hết

**Mục đích:** Kiểm tra cảnh báo khi mức thức ăn thùng chứa thấp.

**Thực hiện:**
- Điều chỉnh HC-SR04 cho khoảng cách xa (thùng gần trống, <20%).

**Kết quả mong đợi:** Hệ thống gửi cảnh báo "hopper_low" qua MQTT. Dashboard hiển thị cảnh báo. Chống spam: chỉ 1 lần / 6 tiếng.

### 2.8.5. Kiểm thử mất kết nối thiết bị

**Mục đích:** Đánh giá khả năng offline-first và phát hiện mất kết nối.

**Thực hiện:**
- Dừng mô phỏng ESP32 trên Wokwi.
- Quan sát trạng thái trên Dashboard.

**Kết quả mong đợi:** Dashboard hiển thị "Offline". Lịch ăn trên ESP32 vẫn hoạt động bình thường (offline-first). Sự kiện được lưu tạm trong hàng đợi LittleFS, gửi lên khi có mạng lại.

---

# CHƯƠNG 3. XÂY DỰNG VÀ TRIỂN KHAI HỆ THỐNG

## 3.1. Mô hình triển khai hệ thống

Để kiểm tra tính khả thi của hệ thống trước khi triển khai trên phần cứng thực tế, nhóm sử dụng nền tảng mô phỏng Wokwi nhằm xây dựng và kiểm thử toàn bộ mô hình IoT. Wokwi cho phép mô phỏng hoạt động của vi điều khiển ESP32 cùng các linh kiện ngoại vi, giúp kiểm tra thuật toán điều khiển và quá trình truyền dữ liệu trước khi lắp đặt thực tế.

Mô hình mô phỏng bao gồm các thành phần:

- **ESP32 DevKit V1** — Vi điều khiển trung tâm
- **Stepper Motor + A4988 Driver** — Cơ cấu nhả thức ăn
- **HX711 + Loadcell 5kg** — Cân nặng thức ăn trong bát
- **HC-SR04** — Đo mức thức ăn thùng chứa
- **DHT22** — Nhiệt độ và độ ẩm
- **OLED SSD1306** — Hiển thị thông tin trên thiết bị
- **RTC DS1307** — Đồng hồ thời gian thực dự phòng
- **Nút nhấn** — Cho ăn thủ công
- **Buzzer** — Cảnh báo âm thanh
- **LED** — Trạng thái hoạt động
- **Kết nối Wi-Fi** → MQTT Broker → FastAPI → Dashboard

Thông qua mô hình này, nhóm có thể đánh giá hoạt động của hệ thống trong nhiều điều kiện khác nhau.

*(Chèn hình ảnh mô hình mô phỏng trên Wokwi tại đây)*

## 3.2. Thiết kế và kết nối phần cứng

Hệ thống bao gồm các thành phần chính được kết nối với vi điều khiển trung tâm như sau:

- **Khối điều khiển trung tâm (Vi điều khiển ESP32):** Đóng vai trò là bộ não của hệ thống, chịu trách nhiệm thu thập dữ liệu từ các cảm biến, xử lý thông tin và xuất tín hiệu điều khiển ra các thiết bị ngoại vi.

- **Khối cân đo khẩu phần (HX711 + Loadcell):** Được sử dụng để đo chính xác trọng lượng thức ăn trong bát. Chân DT (GPIO 16) và SCK (GPIO 4) kết nối với ESP32. Hỗ trợ auto-tare và lọc nhiễu median filter.

- **Khối nhả thức ăn (Stepper Motor + A4988):** Stepper motor quay cơ cấu vít xoắn để nhả thức ăn từ thùng chứa xuống bát. Driver A4988 kết nối với ESP32 qua 3 chân: STEP (GPIO 13), DIR (GPIO 27), ENABLE (GPIO 25). Encoder phản hồi (GPIO 34, 35) xác nhận trục đã quay.

- **Khối đo mức thùng chứa (HC-SR04):** Cảm biến siêu âm gắn trên nắp thùng, hướng xuống để đo khoảng cách đến bề mặt thức ăn. TRIG (GPIO 5), ECHO (GPIO 18).

- **Khối giám sát môi trường (DHT22):** Đo nhiệt độ và độ ẩm không khí để đánh giá điều kiện bảo quản thức ăn. Chân DATA (GPIO 15).

- **Khối hiển thị (OLED SSD1306 + RTC DS1307):** OLED hiển thị giờ, trạng thái mạng, gram bát, % thùng, cữ ăn tiếp theo. RTC dự phòng thời gian khi mất NTP. Kết nối I2C (SDA GPIO 21, SCL GPIO 22).

- **Khối tương tác (Nút nhấn, Buzzer, LED):** Nút nhấn (GPIO 32) cho ăn thủ công. Buzzer (GPIO 23) cảnh báo khi có sự cố. LED (GPIO 2) hiển thị trạng thái.

**Nguyên lý hoạt động của mô hình:**

Trong quá trình hoạt động, ESP32 liên tục đọc dữ liệu từ các cảm biến. Khi đến giờ ăn theo lịch trình hoặc nhận lệnh cho ăn, hệ thống kiểm tra:
1. Bát có còn nhiều thức ăn không (loadcell).
2. Chưa vượt giới hạn ngày (6 lần, 150g).
3. Nếu đạt điều kiện → bật stepper motor, nhả thức ăn từng đợt (200 bước/đợt).
4. Sau mỗi đợt, đọc loadcell để kiểm tra lượng đã nhả.
5. Nếu không tăng qua 3 đợt → phát hiện kẹt → đảo chiều thử → vẫn kẹt → dừng + cảnh báo.
6. Khi đạt đủ gram → dừng motor → gửi sự kiện "fed" qua MQTT.

## 3.3. Thiết kế Giao diện Giám sát Người dùng (Web Dashboard)

Để người dùng có thể dễ dàng theo dõi và quản lý hệ thống từ xa, đề tài đã tiến hành thiết kế và xây dựng một giao diện bảng điều khiển trên nền tảng Web. Giao diện được thiết kế theo xu hướng hiện đại, trực quan và thân thiện với người sử dụng, hỗ trợ cả dark theme và light theme.

Cấu trúc giao diện được chia thành các khối chức năng cốt lõi sau:

- **Header:** Tên hệ thống "Pet Feeder Dashboard", trạng thái kết nối (online/offline) hiển thị dưới dạng pill với chấm tròn nhấp nháy, thời gian cập nhật cuối cùng.

- **Tiles dữ liệu cảm biến:** Bốn thẻ thông tin hiển thị dữ liệu real-time:
  - **Cân nặng bát (g):** Trọng lượng thức ăn hiện có trong bát.
  - **Mức thùng (%):** Phần trăm thức ăn còn trong thùng chứa.
  - **Nhiệt độ (°C):** Nhiệt độ môi trường.
  - **Độ ẩm (%):** Độ ẩm không khí.

- **Nút Feed Now:** Cho ăn từ xa với khẩu phần có thể tùy chỉnh.

- **Lịch ăn:** Bảng hiển thị các cữ ăn đã cài đặt, có thể thêm/sửa/xóa.

- **Biểu đồ:** Đồ thị cân nặng bát theo thời gian để theo dõi xu hướng.

- **Lịch sử cho ăn:** 20 sự kiện gần nhất với thông tin nguồn, kết quả, khẩu phần.

- **Cảnh báo:** Danh sách cảnh báo chưa xử lý.

*(Chèn hình ảnh Web Dashboard tại đây)*

## 3.4. Bảng điều khiển và cấu hình hệ thống

Bên cạnh chức năng giám sát dữ liệu theo thời gian thực, Web Dashboard còn cung cấp bảng điều khiển giúp người dùng quản lý và cấu hình hoạt động của hệ thống.

**a. Cho ăn từ xa**

Người dùng có thể nhấn nút "Feed Now" trên Dashboard để cho ăn ngay lập tức. Hệ thống gửi lệnh qua MQTT topic `petfeeder/device01/command` với payload `{"command":"FEED","amount":30}`.

**b. Quản lý lịch ăn**

Dashboard cho phép người dùng:
- Thêm cữ ăn mới (giờ, phút, gram).
- Bật/tắt từng cữ ăn.
- Xóa cữ ăn.
- Tối đa 6 cữ ăn/ngày.

**c. MQTT Topics chính thức**

| Topic | Hướng | Mô tả |
|---|---|---|
| `petfeeder/device01/status` | ESP32 → Server | "online" hoặc "offline" |
| `petfeeder/device01/event` | ESP32 → Server | Sự kiện cho ăn, cảnh báo |
| `petfeeder/device01/sensor/weight` | ESP32 → Server | Cân nặng bát (gram) |
| `petfeeder/device01/sensor/food_level` | ESP32 → Server | Mức thùng (%) |
| `petfeeder/device01/sensor/env` | ESP32 → Server | Nhiệt độ, độ ẩm |
| `petfeeder/device01/feeding` | ESP32 → Server | Kết quả cho ăn |
| `petfeeder/device01/alert` | ESP32 → Server | Cảnh báo sự cố |
| `petfeeder/device01/command` | Server → ESP32 | Lệnh cho ăn |
| `petfeeder/device01/vision/pet_detected` | Camera → ESP32 | Phát hiện thú cưng |

**d. REST API**

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/health` | GET | Kiểm tra trạng thái server |
| `/api/device/{id}/state` | GET | Trạng thái thiết bị |
| `/api/device/{id}/feed` | POST | Gửi lệnh cho ăn |
| `/api/schedules` | GET/POST | Danh sách/thêm lịch ăn |
| `/api/schedules/{id}` | PUT/DELETE | Sửa/xóa lịch ăn |
| `/api/feedings` | GET | Lịch sử cho ăn |
| `/api/alerts` | GET | Danh sách cảnh báo |
| `/api/sensors` | GET | Dữ liệu cảm biến |
| `/ws` | WebSocket | Dữ liệu real-time |

---

# CHƯƠNG 4. ĐÁNH GIÁ KẾT QUẢ VÀ HƯỚNG PHÁT TRIỂN

## 4.1. Đánh giá kết quả thực hiện

Sau quá trình nghiên cứu, thiết kế và xây dựng mô hình, nhóm đã hoàn thành hệ thống **máy cho thú cưng ăn tự động dựa trên IoT và nhận dạng hình ảnh** trên nền tảng mô phỏng Wokwi kết hợp Backend FastAPI và Web Dashboard. Hệ thống đáp ứng được các yêu cầu đặt ra ban đầu như cho ăn theo lịch trình, cân đo chính xác khẩu phần, giám sát thông số theo thời gian thực và điều khiển từ xa.

Các chức năng chính đã hoàn thành gồm:

- Cho ăn theo lịch trình (tối đa 6 cữ/ngày).
- Cân đo khẩu phần chính xác bằng loadcell HX711.
- Phát hiện kẹt thức ăn (jam detection) và tự động đảo chiều.
- Bỏ qua cữ ăn khi bát còn nhiều thức ăn.
- Giám sát mức thức ăn thùng chứa qua HC-SR04.
- Giám sát nhiệt độ, độ ẩm môi trường qua DHT22.
- Phát hiện thức ăn thiu dựa trên thời gian và điều kiện môi trường.
- Gửi dữ liệu qua MQTT đến Backend FastAPI.
- Lưu trữ dữ liệu vào SQLite.
- Hiển thị dữ liệu real-time trên Web Dashboard qua WebSocket.
- Cho ăn từ xa qua Dashboard.
- Quản lý lịch ăn (thêm/sửa/xóa).
- Xem lịch sử cho ăn và cảnh báo.
- Hiển thị thông tin trên OLED.
- Hoạt động offline-first (lịch ăn chạy khi mất mạng).
- Hàng đợi sự kiện LittleFS (gửi lại khi có mạng).
- Trang demo nhận dạng chó mèo.

Kết quả kiểm thử cho thấy hệ thống hoạt động ổn định trong môi trường mô phỏng và đáp ứng đúng yêu cầu thiết kế của đề tài.

## 4.2. Đánh giá tính khả thi

**Tính khả thi về chi phí phần cứng (giá tham khảo):**

| Thiết bị | Số lượng | Giá tham khảo (VNĐ) |
|---|---|---|
| ESP32 DevKit V1 | 1 | 160.000 |
| ESP32-CAM | 1 | 120.000 |
| Stepper Motor NEMA 17 | 1 | 180.000 |
| A4988 Driver | 1 | 25.000 |
| HX711 + Loadcell 5kg | 1 | 85.000 |
| HC-SR04 | 1 | 25.000 |
| DHT22 | 1 | 80.000 |
| OLED SSD1306 | 1 | 50.000 |
| RTC DS1307 | 1 | 30.000 |
| Encoder quang | 1 | 35.000 |
| Buzzer, nút nhấn, LED | 1 bộ | 20.000 |
| Adapter nguồn 12V | 1 | 80.000 |
| Dây nối và phụ kiện | 1 bộ | 100.000 |
| Khung/vỏ máy | 1 | 150.000 |
| **Tổng cộng** | | **≈1.140.000 VNĐ** |

Nhìn chung, mức chi phí này phù hợp cho mục đích học tập, nghiên cứu và triển khai ở quy mô hộ gia đình.

### 4.2.2. Chi phí vận hành

Chi phí vận hành của hệ thống khá thấp do sử dụng:
- Wi-Fi để truyền dữ liệu.
- Mosquitto MQTT Broker (miễn phí).
- FastAPI + SQLite (miễn phí).
- Motor chỉ hoạt động khi cho ăn (vài phút/ngày).

Vì vậy, chi phí sử dụng hàng tháng gần như không đáng kể.

### 4.2.3. Mức tiêu thụ điện

| Thiết bị | Công suất |
|---|---|
| ESP32 | 1–2 W |
| ESP32-CAM | 1–3 W |
| Stepper Motor (khi hoạt động) | 5–12 W |
| Các cảm biến | <1 W |
| OLED | <0.1 W |

Do stepper motor chỉ hoạt động trong thời gian ngắn (vài phút/ngày) nên hệ thống tiết kiệm điện năng.

### 4.2.4. Đánh giá khả năng và độ ổn định

**a. Đánh giá độ ổn định**

Trong quá trình kiểm thử trên Wokwi, hệ thống hoạt động ổn định với các chức năng chính:
- Đọc dữ liệu cảm biến liên tục.
- Cho ăn đúng khẩu phần theo lịch trình.
- Phát hiện kẹt thức ăn chính xác.
- Đồng bộ dữ liệu với Backend qua MQTT.
- Hiển thị real-time trên Dashboard qua WebSocket.
- Hoạt động offline khi mất kết nối.
- OLED hiển thị thông tin chính xác.

**b. Khả năng triển khai thực tế**

Hệ thống có thể áp dụng cho:
- Hộ gia đình nuôi chó, mèo.
- Cửa hàng thú cưng.
- Trại nuôi quy mô nhỏ.
- Phòng khám thú y.

**Đánh giá tổng quan**

| Tiêu chí | Đánh giá |
|---|---|
| Chi phí đầu tư | Trung bình |
| Chi phí vận hành | Thấp |
| Tiêu thụ điện | Thấp |
| Khả năng giám sát | Tốt |
| Điều khiển từ xa | Tốt |
| Độ chính xác khẩu phần | Cao |
| Khả năng mở rộng | Cao |
| Khả năng ứng dụng | Cao |

## 4.3. Ưu điểm và hạn chế

**a. Ưu điểm**
- Cho ăn tự động theo lịch trình, giảm sự phụ thuộc vào người chủ.
- Cân đo khẩu phần chính xác bằng loadcell.
- Phát hiện kẹt thức ăn và tự động xử lý.
- Giám sát nhiệt độ, độ ẩm bảo quản thức ăn.
- Phát hiện thức ăn thiu.
- Điều khiển từ xa thông qua Web Dashboard.
- Hoạt động offline-first, không phụ thuộc Internet.
- Giao diện trực quan, hỗ trợ dark/light theme.
- Kiến trúc 4 lớp rõ ràng, dễ mở rộng.
- Dữ liệu real-time qua WebSocket.

**b. Hạn chế**
- Camera nhận dạng thú cưng chưa có model YOLO được train.
- Chưa có ứng dụng di động (Flutter app cần cập nhật).
- Firebase push notification chưa cấu hình.
- Chưa hỗ trợ nhận dạng từng thú cưng riêng biệt (RFID/YOLO).
- Mới dừng ở mức mô phỏng trên Wokwi.
- Chưa triển khai phần cứng thực tế.

## 4.4. Hướng phát triển của hệ thống

Trong thời gian tới, hệ thống có thể được mở rộng theo các hướng sau:

- Triển khai trên mô hình phần cứng thực tế với ESP32 và các cảm biến thật.
- Train model YOLO cho ESP32-CAM để nhận dạng thú cưng thực tế.
- Phát triển ứng dụng di động Flutter để điều khiển hệ thống từ xa.
- Tích hợp Firebase Cloud Messaging để gửi push notification.
- Hỗ trợ nhận dạng từng thú cưng riêng biệt bằng RFID hoặc AI Vision.
- Quản lý nhiều máy cho ăn trên cùng một Dashboard.
- Tích hợp thêm cảm biến mực nước bình uống.
- Tích hợp cảm biến cân nặng thú cưng để theo dõi sức khỏe.
- Thông báo qua Email hoặc Telegram khi có sự cố.
- Sử dụng năng lượng pin dự phòng để hoạt động khi mất điện.
- Triển khai Backend trên cloud (Docker + PostgreSQL) cho truy cập từ xa qua Internet.

---

# KẾT LUẬN

Đề tài **"Máy cho thú cưng ăn tự động dựa trên IoT và nhận dạng hình ảnh"** đã hoàn thành các mục tiêu đề ra trong phạm vi nghiên cứu. Nhóm đã xây dựng thành công mô hình mô phỏng trên nền tảng Wokwi, kết hợp vi điều khiển ESP32, cảm biến loadcell HX711, cảm biến siêu âm HC-SR04, cảm biến DHT22, Stepper Motor A4988, MQTT Broker Mosquitto, Backend FastAPI + SQLite và Web Dashboard để tạo thành một hệ thống giám sát và điều khiển cho thú cưng ăn thông minh.

Kết quả mô phỏng cho thấy hệ thống có khả năng cho ăn theo lịch trình đã cài đặt, cân đo chính xác khẩu phần thức ăn, phát hiện kẹt thức ăn, giám sát mức thùng chứa và điều kiện môi trường, đồng thời cho phép người dùng giám sát và điều khiển từ xa thông qua giao diện Web. Thiết kế offline-first đảm bảo hệ thống vẫn hoạt động ổn định khi mất kết nối Internet.

Mặc dù hệ thống mới được triển khai trong môi trường mô phỏng, các kết quả đạt được đã chứng minh tính khả thi của giải pháp và tạo nền tảng để phát triển thành một hệ thống thực tế trong tương lai. Với chi phí đầu tư hợp lý, khả năng mở rộng cao và ứng dụng các công nghệ IoT hiện đại, đề tài có tiềm năng áp dụng trong các hộ gia đình nuôi thú cưng, góp phần thúc đẩy quá trình ứng dụng công nghệ vào lĩnh vực chăm sóc thú cưng thông minh.

---

# LỜI KẾT THÚC

Đề tài **"Máy cho thú cưng ăn tự động dựa trên IoT và nhận dạng hình ảnh"** đã giúp nhóm vận dụng những kiến thức đã học về Internet of Things (IoT), vi điều khiển, mạng truyền thông, cơ sở dữ liệu và phát triển ứng dụng Web vào việc giải quyết một bài toán thực tiễn trong lĩnh vực chăm sóc thú cưng thông minh.

Trong quá trình thực hiện, nhóm đã tiến hành khảo sát nhu cầu thực tế, phân tích yêu cầu hệ thống, lựa chọn các công nghệ phù hợp như ESP32, Loadcell HX711, Stepper Motor, giao thức MQTT, FastAPI và SQLite để xây dựng mô hình hệ thống cho thú cưng ăn tự động. Đồng thời, nhóm cũng thiết kế kiến trúc tổng thể 4 tầng, mô hình dữ liệu và quy trình xử lý nhằm đảm bảo hệ thống có khả năng giám sát, điều khiển từ xa và tự động đưa ra quyết định cho ăn dựa trên dữ liệu cảm biến kết hợp với nhận dạng hình ảnh thú cưng.

Mặc dù đã nỗ lực hoàn thành đề tài với tinh thần nghiêm túc và trách nhiệm, do giới hạn về thời gian, kinh nghiệm cũng như điều kiện triển khai thực tế nên báo cáo vẫn còn một số hạn chế và cần tiếp tục được hoàn thiện trong các giai đoạn tiếp theo. Nhóm rất mong nhận được những ý kiến đóng góp quý báu từ quý thầy cô để có thể bổ sung, chỉnh sửa và phát triển hệ thống một cách hoàn thiện hơn.

Nhóm xin chân thành cảm ơn giảng viên hướng dẫn cùng quý thầy cô trong Khoa Công nghệ Thông tin, Trường Đại học Công Thương Thành phố Hồ Chí Minh đã tận tình hướng dẫn, truyền đạt kiến thức và tạo điều kiện thuận lợi để nhóm hoàn thành đồ án này.

**Một lần nữa, nhóm xin chân thành cảm ơn!**

---

# TÀI LIỆU THAM KHẢO

1. **[1]** Espressif Systems, *ESP32 Programming Guide*, Espressif Systems, 2025.
   Truy cập: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/
   Thời gian truy cập: 17/07/2026.

2. **[2]** HiveMQ GmbH, *MQTT Essentials – A Lightweight IoT Protocol*, 2024.
   Truy cập: https://www.hivemq.com/mqtt/
   Thời gian truy cập: 17/07/2026.

3. **[3]** Eclipse Foundation, *Eclipse Mosquitto MQTT Broker Documentation*, 2025.
   Truy cập: https://mosquitto.org/
   Thời gian truy cập: 17/07/2026.

4. **[4]** Sebastián Ramírez, *FastAPI Documentation*, 2025.
   Truy cập: https://fastapi.tiangolo.com/
   Thời gian truy cập: 17/07/2026.

5. **[5]** SQLite Consortium, *SQLite Documentation*, 2025.
   Truy cập: https://www.sqlite.org/docs.html
   Thời gian truy cập: 17/07/2026.

6. **[6]** Arduino, *Arduino Documentation*, Arduino AG, 2025.
   Truy cập: https://docs.arduino.cc/
   Thời gian truy cập: 17/07/2026.

7. **[7]** Random Nerd Tutorials, *ESP32 IoT Projects and Tutorials*, Rui Santos & Sara Santos, 2025.
   Truy cập: https://randomnerdtutorials.com/projects-esp32/
   Thời gian truy cập: 17/07/2026.

8. **[8]** PlatformIO Labs, *PlatformIO Documentation*, 2025.
   Truy cập: https://docs.platformio.org/
   Thời gian truy cập: 17/07/2026.

9. **[9]** Wokwi, *Wokwi Simulator Documentation*, 2025.
   Truy cập: https://docs.wokwi.com/
   Thời gian truy cập: 17/07/2026.

10. **[10]** Trường Đại học Công Thương Thành phố Hồ Chí Minh, *Giáo trình Internet of Things (IoT)*, Khoa Công nghệ Thông tin, 2025.
