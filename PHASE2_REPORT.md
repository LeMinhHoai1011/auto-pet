# Phase 2 — AI Recognition Pipeline — Completion Report

## Tổng quan

Phase 2 triển khai module nhận diện danh tính mèo độc lập, chạy ở chế độ **shadow/observe** (chỉ quan sát, không kích hoạt cho ăn). Toàn bộ code Phase 1 (ESP32 firmware, MQTT, dashboard, API hiện tại) được giữ nguyên 100%.

## Kiến trúc AI Pipeline

```
Camera → YOLOv8n (detect cat) → ByteTrack (tracking) → Haar Cascade (face crop)
  → Quality Filter (blur/brightness/size) → DINOv2 (embedding 384-dim)
  → Cosine Similarity Matcher → Vote-based Confirmation → Log/Collect
```

## Models đã chọn

| Component | Model | License | Lý do |
|-----------|-------|---------|-------|
| Cat Detection | YOLOv8n (COCO class 15) | AGPL-3.0 | Nhẹ, chính xác, pip install |
| Tracking | ByteTrack (supervision) | MIT | Đa đối tượng, ổn định |
| Face Detection | OpenCV Haar Cascade | BSD | Có sẵn, không cần download |
| Embedding | DINOv2 ViT-S/14 (Meta) | Apache-2.0 | Fine-grained features, không cần train |

**PetFace**: Đã nghiên cứu nhưng GitHub repo trả 404 → loại bỏ, thay bằng DINOv2.

## Files mới tạo (Phase 2)

### Recognition Module (`server/app/recognition/`)
| File | Chức năng |
|------|-----------|
| `config.py` | Toàn bộ cấu hình qua env vars |
| `detector.py` | YOLO cat detection, ROI filtering |
| `tracker.py` | ByteTrack multi-object tracking |
| `face_detector.py` | Haar cascade face detection + fallback body crop |
| `quality_filter.py` | Blur/brightness/size check, pHash dedup |
| `embedding.py` | DINOv2 embedding extraction (384-dim) |
| `matcher.py` | Cosine similarity matching, EmbeddingStore |
| `registry.py` | Pet image save/process/rebuild |
| `collector.py` | Session-based auto image collection |
| `camera.py` | Multi-source camera manager (webcam/URL/file) |
| `pipeline.py` | Main orchestration: OFF/OBSERVE/REGISTER modes |

### API Endpoints (`server/app/routers/`)
| File | Endpoints |
|------|-----------|
| `pets.py` | CRUD pets, upload images, rebuild embeddings |
| `recognition.py` | Pipeline control, MJPEG stream, identify, sessions, logs |

### Database Models (thêm vào `models.py`)
- `Pet` — Thông tin mèo + cấu hình cho ăn riêng
- `PetImage` — Ảnh đã lưu (upload/session/camera)
- `PetEmbedding` — Vector embedding 384-dim (LargeBinary)
- `RecognitionSession` — Phiên quan sát mèo
- `RecognitionSample` — Ảnh mẫu trong phiên
- `RecognitionLog` — Lịch sử nhận diện

### Dashboard & Scripts
| File | Mô tả |
|------|-------|
| `dashboard/ai-recognition.html` | Trang kiểm thử AI: video stream, stats, pet registry, sessions, logs |
| `setup.ps1` | Tạo venv, cài dependencies, tạo thư mục |
| `download-models.ps1` | Tải trước YOLOv8n + DINOv2 |
| `start.ps1` | Khởi chạy server |

## Files đã sửa

| File | Thay đổi |
|------|----------|
| `server/app/main.py` | Import routers mới, load embedding store on startup, cleanup on shutdown, route `/ai`, mount `/storage` |
| `server/app/models.py` | Thêm 6 bảng mới (Pet, PetImage, PetEmbedding, RecognitionSession, RecognitionSample, RecognitionLog) |
| `server/app/schemas.py` | Thêm Pydantic schemas cho pets/recognition |
| `server/requirements.txt` | Thêm torch, torchvision, ultralytics, supervision, opencv-python-headless, python-multipart |

## API Endpoints mới (20 endpoints)

### Pets (`/api/pets/`)
- `GET /api/pets/` — Danh sách pets
- `POST /api/pets/` — Tạo pet mới
- `GET /api/pets/{id}` — Chi tiết pet
- `PATCH /api/pets/{id}` — Cập nhật pet
- `DELETE /api/pets/{id}` — Vô hiệu hóa (soft delete)
- `POST /api/pets/{id}/images` — Upload ảnh (multi-file)
- `GET /api/pets/{id}/images` — Danh sách ảnh
- `DELETE /api/pets/{id}/images/{img_id}` — Xóa ảnh
- `POST /api/pets/{id}/embeddings/rebuild` — Rebuild embeddings

### Recognition (`/api/recognition/`)
- `GET /api/recognition/status` — Trạng thái pipeline
- `POST /api/recognition/start?mode=observe` — Bắt đầu AI
- `POST /api/recognition/stop` — Dừng AI
- `GET /api/recognition/stream` — MJPEG video stream
- `POST /api/recognition/identify` — Nhận diện từ ảnh đơn
- `GET /api/recognition/sessions` — Danh sách phiên
- `GET /api/recognition/sessions/{id}` — Chi tiết phiên
- `POST /api/recognition/sessions/{id}/assign` — Gán phiên cho pet
- `POST /api/recognition/sessions/{id}/reject` — Từ chối phiên
- `GET /api/recognition/logs` — Lịch sử nhận diện

## Verification

- **Import test**: Tất cả 12 module recognition + schemas + models import thành công
- **Route registration**: 43 routes total, 20 AI-related endpoints registered
- **Safety**: Pipeline chỉ chạy ở OBSERVE mode; Active mode trả lỗi "not available in Phase 2"
- **Không ảnh hưởng Phase 1**: Firmware, MQTT topics, dashboard gốc, API hiện tại — không thay đổi

## Hướng dẫn chạy

```powershell
cd server
.\setup.ps1              # Tạo venv + cài dependencies
.\download-models.ps1    # Tải AI models (lần đầu)
.\start.ps1              # Chạy server

# Truy cập
# Dashboard:  http://localhost:8000/
# AI Test:    http://localhost:8000/ai
# API Docs:   http://localhost:8000/docs
```

## Giới hạn & Lưu ý

1. **Shadow mode only** — Pipeline KHÔNG gửi lệnh cho ăn, chỉ quan sát và log
2. **Chưa có torch/ultralytics trong venv** — Cần chạy `setup.ps1` để cài đầy đủ
3. **GPU optional** — Tự detect CUDA, fallback CPU
4. **ESP32-CAM topic `pet_detected`** — Vẫn là generic detection, không trigger identity-based feeding
5. **Chưa tích hợp MQTT publish** — Recognition results chỉ lưu DB + hiển thị dashboard

## Các bước tiếp theo (Phase 3+)

1. Test thực tế với webcam + ảnh mèo thật
2. Tích hợp MQTT publish recognition results
3. Chuyển sang ACTIVE mode khi pipeline đã kiểm chứng
4. Identity-based feeding logic trên ESP32
5. Flutter app integration
