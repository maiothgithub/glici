"""Module providing a function socket send and receive."""
import socket
import struct

HOST = "0.0.0.0"
PORT = 8080

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
                temperature, humidity, counter = struct.unpack('<ffi', data)
                print(f"Temp: {temperature:.2f}, Hum: {humidity:.2f}, IRSensor: {counter}")
            else:
                print(f"Incorrect packet ({len(data)} bytes)")
            if data:
                print(f"Received: {data.strip()}")
                conn.sendall(b"OK\n")
