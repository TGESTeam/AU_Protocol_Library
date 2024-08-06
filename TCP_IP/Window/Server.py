import socket
import subprocess

import numpy as np

def get_ethernet_mtu():
    try:
        # netsh 명령어 실행 (cp949 인코딩으로 실행)
        result = subprocess.run(["netsh", "interface", "ipv4", "show", "interfaces"], capture_output=True, text=True, encoding='cp949')
        output = result.stdout

        # 결과를 라인별로 나누기
        lines = output.splitlines()
        # 헤더와 데이터 부분 분리
        header_index = next(i for i, line in enumerate(lines) if "MTU" in line)
        data_lines = lines[header_index + 1:]

        # "이더넷" 인터페이스의 MTU 값을 찾기
        for line in data_lines:
            columns = line.split()
            print("col :" + str(columns))
            if len(columns) >= 4:
                if "이더넷" in columns:
                    try:
                        mtu = int(columns[2])
                        print("이더넷 인터페이스의 MTU 값:", mtu)
                        return mtu
                    except ValueError:
                        continue
                elif "Wi-FI" in columns:
                    try:
                        mtu = int(columns[2])
                        print("WI-FI 인터페이스의 MTU 값:", mtu)
                        return mtu
                    except ValueError:
                        continue

        # "이더넷" 인터페이스를 찾지 못하면 기본값 반환
        return 1500
    except Exception as e:
        print(f"Failed to get MTU: {e}")
        return 1500  # 기본값

def start_server():
    # 최대 MTU 값 가져오기
    max_mtu = get_ethernet_mtu()
    print(f"Using max MTU value: {max_mtu}")

    # 소켓 생성
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(1)  # 하나의 클라이언트만 허용
    print("Server started and listening on port 12345")

    # 클라이언트 연결 대기
    client_socket, addr = server.accept()
    print(f"Accepted connection from {addr}")

    while True:
        try:
            # 클라이언트로부터 데이터 수신 (버퍼 사이즈를 max_mtu로 설정)
            data = client_socket.recv(max_mtu).decode('utf-8')
            if not data:
                break
            
            print(f"Received request: {data}")

            # 받은 데이터를 그대로 클라이언트에 응답
            # print(f"Sent response: {data}")
            # SL50000SH10,50,30,5PV1.333,2.333,3.333,4.4444,5.5555,6.6666
            #double_ranom_np = np.random.rand(62500)
            double_ranom_np = np.random.rand(114576 )
            str2 = ",".join([f"{x:.18f}" for x in double_ranom_np])
            str2 = "SL50000" + str2
                
            #print(len(str))
            #print(len(str))
            print(f"Sent response: {len(str2)}")
            client_socket.send(str2.encode('utf-8'))


        except Exception as e:
            print(f"Exception: {e}")
            break

    client_socket.close()
    server.close()
    print("Server closed")

if __name__ == "__main__":
    start_server()
    


# #recv 사이즈를 수동으로 지정해주는 방법

# import socket

# def start_server():
#     # 소켓 생성
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind(('0.0.0.0', 12345))
#     server.listen(1)  # 하나의 클라이언트만 허용
#     print("Server started and listening on port 12345")

#     # 클라이언트 연결 대기
#     client_socket, addr = server.accept()
#     print(f"Accepted connection from {addr}")

#     while True:
#         try:
#             # 클라이언트로부터 데이터 수신
#             data = client_socket.recv(1024).decode('utf-8')
#             if not data:
#                 break
            
#             print(f"Received request: {data}")

#             # 받은 데이터를 그대로 클라이언트에 응답
#             client_socket.send(data.encode('utf-8'))
#             print(f"Sent response: {data}")

#         except Exception as e:
#             print(f"Exception: {e}")
#             break

#     client_socket.close()
#     server.close()
#     print("Server closed")

# if __name__ == "__main__":
#     start_server()

