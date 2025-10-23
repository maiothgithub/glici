"""Module providing a function socket send and receive."""
import socket
import struct
import sqlite3
from datetime import datetime

HOST = "0.0.0.0"
PORT = 8080

DB_FILE = "sensor_data.db"

# --- Setup database ---
dbconn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = dbconn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    temperature REAL,
    humidity REAL,
    sensor INTEGER
)
""")
dbconn.commit()

def insert_reading(temp, hum, sensor):
    """Insert a new reading into the database."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO readings (timestamp, temperature, humidity, sensor) VALUES (?, ?, ?, ?)",
        (ts, temp, hum, sensor)
    )
    dbconn.commit()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            data = conn.recv(1024)
            if len(data) == 12:
                # '<' = little endian, 'ff' = two floats, 'i' = int32
                temperature, humidity, irsensor = struct.unpack('<ffi', data)
                insert_reading(temperature, humidity, irsensor)
                print(f"Temp: {temperature:.2f}, Hum: {humidity:.2f}, IRSensor: {irsensor}")
            else:
                print(f"Incorrect packet ({len(data)} bytes)")
            if data:
                print(f"Received: {data.strip()}")
                conn.sendall(b"OK\n")
