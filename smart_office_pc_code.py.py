import serial
import requests
import time
import cv2

# ================= CONFIG =================

AIO_USERNAME = "Enter_YOUR_adafruit_username"
AIO_KEY = "Enter_your_adafruit_KEY"

BOT_TOKEN = "Enter_the_telegram_BOT_TOKEN "
CHAT_ID = "Enter_telegram_CHAT_ID"

SERIAL_PORT = "Enter_serial_port_ex_COM7"
BAUD_RATE = 9600

# ================= SERIAL =================

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

print("SMART OFFICE SYSTEM RUNNING...")

# ================= AIO FUNCTION =================

def send_to_aio(feed, value):
    url = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{feed}/data"

    headers = {
        "X-AIO-Key": AIO_KEY,
        "Content-Type": "application/json"
    }

    data = {"value": str(value)}

    try:
        res = requests.post(url, json=data, headers=headers)

        if res.status_code == 200:
            print(f"✅ {feed} → {value}")
        else:
            print(f"❌ {feed} ERROR → {res.status_code} | {res.text}")

    except Exception as e:
        print("AIO Error:", e)

# ================= TELEGRAM =================

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
        print("📩 Telegram sent")

    except Exception as e:
        print("Telegram Error:", e)

# ================= CAMERA =================

def capture_photo(name):
    try:
        cam = cv2.VideoCapture(0)
        time.sleep(1)

        ret, frame = cam.read()

        if ret:
            filename = f"{name}_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 Photo saved: {filename}")

        cam.release()

    except Exception as e:
        print("Camera Error:", e)

# ================= MAIN LOOP =================

while True:
    try:
        if ser.in_waiting:
            line = ser.readline().decode().strip()
            print("Received:", line)

            # ================= USER ENTRY =================
            if line.startswith("CAPTURE"):
                parts = line.split(":")

                if len(parts) == 4:
                    name = parts[1]
                    status = parts[2]
                    count = int(parts[3])

                    print(f"{name} {status} | Count: {count}")

                    # 🔥 AIO (ALL FEEDS)
                    send_to_aio("smart-office.last-user", name)
                    send_to_aio("smart-office.last-status", status)
                    send_to_aio("smart-office.occupancy-count", int(count))
                    send_to_aio("smart-office.last-action", f"{name} {status}")

                    # Telegram
                    send_telegram(f"{name} {status} | Count: {count}")

                    # Camera
                    capture_photo(name)

                else:
                    print("❌ Invalid CAPTURE format")

            # ================= ASSET =================
            elif line.startswith("ASSET"):
                parts = line.split(":")

                if len(parts) == 2:
                    asset = parts[1]

                    print(f"Asset: {asset}")

                    send_to_aio("smart-office.last-asset", asset)
                    send_to_aio("smart-office.last-action", asset)

                else:
                    print("❌ Invalid ASSET format")

            # ================= UNAUTHORIZED =================
            elif line.startswith("UNAUTHORIZED"):
                print("🚨 Unauthorized Access!")

                send_to_aio("smart-office.security-alerts", "Unauthorized")
                send_telegram("🚨 Unauthorized Access Detected!")

            else:
                print("⚠ Unknown data")

    except Exception as e:
        print("Error:", e)

    time.sleep(0.1)