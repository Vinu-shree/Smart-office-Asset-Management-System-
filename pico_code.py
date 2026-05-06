from mfrc522 import MFRC522
import utime
from machine import Pin
import sys
import uselect as select

# ---------------- PINS ----------------
red = Pin(17, Pin.OUT)
green = Pin(16, Pin.OUT)
buzzer = Pin(15, Pin.OUT)
relay = Pin(14, Pin.OUT)

# ---------------- RFID ----------------
rfid_reader = MFRC522(
    spi_id=0,
    sck=2,
    miso=4,
    mosi=7,
    cs=5,
    rst=18
)

# ---------------- USERS ----------------
users = {
    1559419218: "Vinushree",
    1554502242: "Visitor",
    1548903522: "Staff_1"
}

# ---------------- ASSETS ----------------
assets = {
    78302617: "Dell Laptop",
    374005299: "Projector",
    105901521: "Tool Kit"
}

# ---------------- VARIABLES ----------------
last_card = None
inside_users = set()
occupied_count = 0

# ---------------- FUNCTIONS ----------------
def beep(t=1):
    for _ in range(t):
        buzzer.value(1)
        utime.sleep(0.12)
        buzzer.value(0)
        utime.sleep(0.12)

def burglar_alarm():
    for _ in range(8):
        red.value(1)
        buzzer.value(1)
        utime.sleep(0.25)
        red.value(0)
        buzzer.value(0)
        utime.sleep(0.15)

def valid_access(name):
    global occupied_count

    if name not in inside_users:
        inside_users.add(name)
        occupied_count += 1
        status = "Entered"
    else:
        inside_users.remove(name)
        occupied_count -= 1
        status = "Exited"

    print("CAPTURE:{}:{}:{}".format(name, status, occupied_count))

    green.value(1)
    relay.value(1)
    beep(1)
    utime.sleep(1)
    green.value(0)
    relay.value(0)

def asset_detect(name):
    print("ASSET:" + name)
    green.value(1)
    beep(1)
    utime.sleep(0.3)
    green.value(0)

def invalid_access():
    print("UNAUTHORIZED")
    red.value(1)
    beep(2)
    utime.sleep(0.8)
    red.value(0)

def read_rfid():
    rfid_reader.init()
    status, _ = rfid_reader.request(rfid_reader.REQIDL)

    if status == rfid_reader.OK:
        status, uid = rfid_reader.SelectTagSN()

        if status == rfid_reader.OK:
            return int.from_bytes(bytes(uid), "little")

    return None

print("Final Stable Smart Pico Ready")

# ---------------- LOOP ----------------
while True:

    # Read laptop command safely
    try:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            cmd = sys.stdin.readline().strip()

            if cmd == "ALARM":
                burglar_alarm()
                last_card = None

    except:
        pass

    # RFID scan
    card = read_rfid()

    if card is not None and card != last_card:

        last_card = card

        if card in users:
            valid_access(users[card])

        elif card in assets:
            asset_detect(assets[card])

        else:
            invalid_access()

    if card is None:
        last_card = None

    utime.sleep(0.12)