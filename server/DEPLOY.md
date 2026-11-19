# Deploy Pet Feeder Server — Ubuntu

## Yeu cau
- Ubuntu 22.04+ (hoac WSL2)
- Docker + Docker Compose

## Buoc 1: Cai Docker

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Dang xuat va dang nhap lai
```

## Buoc 2: Copy folder server/ len Ubuntu

```bash
scp -r server/ user@192.168.1.100:~/pet-feeder/
```

## Buoc 3: Cau hinh

```bash
cd ~/pet-feeder
cp .env.example .env
nano .env   # Sua mat khau PostgreSQL, MQTT, SECRET_KEY
```

### Cau hinh MQTT password (bat buoc)

```bash
# Tao password file dung dinh dang Mosquitto
docker run --rm -v $(pwd)/mosquitto:/mosquitto/config \
  eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd mqtt_user mqtt_pass
```

### Firebase (tuy chon — cho push notification)

1. Vao Firebase Console > Project Settings > Service Accounts
2. Generate new private key → tai file JSON
3. Dat ten `firebase-credentials.json` va copy vao folder server/

## Buoc 4: Khoi dong

```bash
docker compose up -d
```

Kiem tra:
```bash
docker compose ps          # Tat ca Running
docker compose logs api    # Xem log FastAPI
docker compose logs mosquitto  # Xem log MQTT
curl http://localhost/api/health  # {"status":"ok"}
```

## Buoc 5: Cau hinh ESP32

Sua `include/secrets.h`:
```cpp
const char MQTT_HOST[] = "192.168.1.100";  // IP Ubuntu server
const int  MQTT_PORT   = 1884; // Host port mapped to broker container port 1883
const char MQTT_USER[] = "mqtt_user";
const char MQTT_PASS[] = "mqtt_pass";
```

## API Endpoints

| Method | URL | Mo ta |
|--------|-----|-------|
| GET | /api/health | Kiem tra server |
| GET | /api/device/status | Trang thai thiet bi |
| POST | /api/feed/ | Cho an tu xa `{"grams": 30}` |
| POST | /api/feed/tare | Tare can |
| GET | /api/feed/history | Lich su cho an |
| GET | /api/schedule/ | Xem lich |
| POST | /api/schedule/ | Them lich `{"hour":7,"minute":0,"grams":30}` |
| PUT | /api/schedule/{id} | Sua lich |
| DELETE | /api/schedule/{id} | Xoa lich |
| GET | /api/alerts/ | Xem canh bao |
| PUT | /api/alerts/{id}/resolve | Danh dau da xu ly |
| GET | /api/sensors/?sensor_type=weight | Lich su cam bien |
| POST | /api/push/register | Dang ky FCM token |

Swagger UI: http://192.168.1.100/docs

## Luong du lieu

```
ESP32 → MQTT publish → Mosquitto broker
                            ↓
                    FastAPI (subscribe)
                            ↓
                    PostgreSQL (luu tru)
                            ↓
                    Firebase → Push notification → Flutter App

Flutter App → REST API → FastAPI → MQTT publish → ESP32
```
