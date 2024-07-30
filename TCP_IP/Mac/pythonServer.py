import socket
import struct
import numpy as np

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080
BUFFER_SIZE = 1024

def receive_3d_data(conn):
    # 데이터 크기 수신
    total_size_data = conn.recv(4)
    total_size = struct.unpack('i', total_size_data)[0]
    
    # 데이터 수신
    data = bytearray()
    while len(data) < total_size:
        packet = conn.recv(BUFFER_SIZE)
        if not packet:
            break
        data.extend(packet)

    # 수신한 데이터를 numpy 배열로 변환
    data = np.frombuffer(data, dtype=np.float64)
    
    # 3차원 배열로 변환 (예제에서는 4x4x4)
    data = data.reshape((4, 4, 4))
    
    print("Received 3D data:")
    print(data)

    # 클라이언트에 확인 메시지 전송
    conn.sendall(b"3D data received successfully.")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(1)
        print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(BUFFER_SIZE)
                    if not data:
                        break
                    
                    try:
                        message = data.decode()
                        if message == "send3d":
                            receive_3d_data(conn)
                        else:
                            print(f"Received message: {message}")
                            conn.sendall(b"Message received successfully.")
                    except UnicodeDecodeError:
                        # 메시지를 디코딩할 수 없는 경우 처리
                        print("Received non-text data, skipping...")
                        continue

if __name__ == "__main__":
    main()
