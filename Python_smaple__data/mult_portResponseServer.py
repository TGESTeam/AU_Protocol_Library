import socket
import threading
import numpy as np
import cv2
from datetime import datetime
import re

print("Load and print the numpy file")
load_py = np.load('C:/UnrealData/apartment_multi_7.npy')
print(load_py.shape)

lock = threading.Lock()

def get_time_index(time:float, time_step:float=0.5)->int:
    """
    시간을 인덱스로 변환하는 함수P
    Args:
        time(float): 시간
        time_step(float): 시간 간격
    
    Returns: 
        int: 시간 인덱스
    """
    MAX_TIME_INDEX = 601 # max_time index
    if time < 0:
        return 0
    if time / time_step > MAX_TIME_INDEX:
        return MAX_TIME_INDEX
    return int(time / time_step)

time = -1
kind = 1
#PV port 8081
flattened_array = load_py[kind, :, :, :, time]


#port 8081
x, y, z = 10, 10, 10

# 이전 버전
# re_flattened_array = flattened_array[x:x+10, y:y+10, z:z+5].reshape(-1) 


def get_8081_ready_data(load_py, kind:int, time:float, user_x:int, user_y:int, user_z:int, x_size:int=10, y_size:int=10, z_size:int=5)->str:
    """
    8081 포트에 대한 데이터를 반환하는 함수
    Args:
        load_py(np.ndarray): 로드된 numpy array
        kind(int): 종류
        time(float): 시간
        user_x(int): 사용자의 x 위치
        user_y(int): 사용자의 y 위치
        user_z(int): 사용자의 z 위치
        x_size(int): x 크기
        y_size(int): y 크기
        z_size(int): z 크기
    
    Returns:
        str: 8081 포트에 대한 데이터
    """
    print('8081 load_py 접근: ', load_py.shape)
    print('8081 parameter: ', kind, time, user_x, user_y, user_z, x_size, y_size, z_size)
    x_start = user_x - 4
    y_start = user_y - 4
    z_start = user_z - 6
    x_end = x_start + x_size
    y_end = y_start + y_size
    z_end = z_start + z_size

    print('8081', 'x_start:', x_start, 'x_end:', x_end, 'y_start:', y_start, 'y_end:', y_end, 'z_start:', z_start, 'z_end:', z_end)
    
    
    save_array = load_py[kind, :, :, :, get_time_index(time)]
    save_array = np.rot90(save_array, 1, axes=(0,2))
    result = np.ones((10, 10, 5))
    save_array = save_array[x_start:x_end, y_start:y_end, save_array.shape[2]-z_end:save_array.shape[2]-z_start]
    for x in range(x_size):
        for y in range(y_size):
            # z는 거꾸로 접근
            for z in range(z_size):
                print('8081', x, y, z_size-z-1) 
                print('8081', x, y, z, save_array.shape)
                print('8081', result.shape)
                result[x, y, z_size-z-1] = save_array[x, y, z]
    print('8081 result_shape', result.shape)
    
    return ",".join(map(str, result.reshape(-1)))

def get_8083_ready_data(load_py, kind:int, time:float, select:int)->str:
    """
    8081 포트에 대한 데이터를 반환하는 함수
    Args:
        load_py(np.ndarray): 로드된 numpy array
        kind(int): 종류
        time(float): 시간
        select(int): 선택 x = 0, y = 1, z = 2
    
    Returns:
        str: 8081 포트에 대한 데이터
    """    
    # print('8083 load_py 접근: ', load_py.shape)
    with lock:
        save_array = load_py[kind, :, :, :, get_time_index(time)]
    
    axes = [2, 1, 0]
    
    temp = np.rot90(save_array, 1, axes=(0,2))
    temp = temp.max(axis=axes[select])
    # print('8083 temp max shape', temp.shape)
    temp = cv2.resize(temp, (100, 100), interpolation=cv2.INTER_LINEAR)
    # print('8083 temp resize shape', temp.shape)

    # print('8083 temp shape', temp.shape)

    
    return ",".join(map(str, temp.reshape(-1)))

check = True
# co, co2, o2, Fuel, 속도(Velocity), 불, 온도

def handle_client(client_socket, server_id, port):
    global check
    while True:
        try:
            message = client_socket.recv(3000).decode('utf-8')
            if not message:
                print(f"Server {server_id}  8083 received: break")
                break
            if port == 8081: # 완성
                print(f"Server {server_id} 8081 received: {message}")
                # KI0000000LO~~~~~TI~~~~~~
                # KI0000000LO890.000000,850.000000,158.337502TI00:00:01.393 
                message = message[:-1]
                KI_str, LO_str, TI_str = [segment for segment in re.split(r'[a-zA-Z]', message) if segment]
                kind_select_index = 0 
                for i in range(len(KI_str)):
                    if KI_str[i] == '1':
                        kind_select_index = i
                        break

                kind_index = [1, 2, 0, 6, 4, 5, 3]
                # print('LO_str: ', list(map(int, LO_str.split(','))))

                x, y, z = [int(float(i)) for i in LO_str.split(',')]
                time_split = TI_str.split(':')
                time = float(time_split[0]) * 3600 + float(time_split[1]) * 60 + float(time_split[2])
                # with lock: # mutex lock 추가
                parshing = "PV" + get_8081_ready_data(load_py, kind_index[kind_select_index], time, x, y, z)
                # print("8081 parshing " + parshing)
                
                #print("parshing " + parshing)
                client_socket.send(parshing.encode('utf-8'))
            elif port == 8082:
                print(f"Server {server_id} 8082 acknowledges: {message}")
                KIND_PV_LENGTH = 7
                # 'KI' 위치 찾기
                message_idx = message.find('KI')

                # 초기 변수 선언
                kind_pv_arr = []
                location_xyz = []
                now_time_str = ""
                future_time_str = ""
                
                # 'KI'가 있는지 확인
                if message_idx != -1:
                    # 구독된 Kind PV를 담음
                    kind_pv_arr = message[(message_idx + 2):(message_idx + 2 + KIND_PV_LENGTH)]
                    message_idx += 2 + KIND_PV_LENGTH

                    # 'TN' 위치 찾기
                    end_idx = message.find('TN')

                    # TN이 존재할 경우
                    if end_idx != -1:
                        message_idx += 2
                        # 사용자의 위치가 담긴 location 배열
                        location_xyz_str = message[message_idx:end_idx - 1].split(',')
                        
                        if len(location_xyz_str) >= 3:  # 위치 값이 세 개 이상일 경우에만 처리
                            location_xyz_str = np.array(location_xyz_str, dtype=float)
                            location_xyz = np.floor(location_xyz_str)
                        else:
                            print("Invalid location data, using default [0, 0, 0]")  # 위치 데이터가 없을 때 경고 출력
                        
                        # TN 이후 부분에서 시간 정보 찾기
                        message_idx = end_idx + 2
                        for i in range(message_idx, len(message)):
                            if message[i] != 'T':
                                end_idx = i
                            else:
                                break
                        
                        # 시간 정보 문자열을 추출
                        now_time_str = message[message_idx:end_idx]
                        print(f"Extracted now_time_str: {now_time_str}")  # 디버깅 출력
                        
                        if not now_time_str:  # now_time_str가 빈 문자열일 경우 기본값 설정
                            now_time_str = "00:00:00.000"
                            print("now_time_str is empty, setting default value '00:00:00.000'")
                        
                        if end_idx != len(message):
                            future_time_str = message[end_idx + 3:]         
                future_time_str = future_time_str.replace('\x00', '')  # 널 문자를 제거
                future_time = int(future_time_str) 
                check = 0
                for i in range(1, 6):
                    addition = int(future_time // 5)
                    if addition == 0:
                        addition = 1
                        check += 1
                        break
                    check += 1
                    
                if check != 1:
                    check += 1
                        

                response = ""
                try:
                    parsed_time = datetime.strptime(now_time_str, "%H:%M:%S.%f")
                except ValueError as e:
                    print(f"Error parsing time: {e}")
                    parsed_time = datetime.strptime("00:00:00.000", "%H:%M:%S.%f")  # 기본값
                total_seconds = int(parsed_time.hour * 3600 + parsed_time.minute * 60 + parsed_time.second + parsed_time.microsecond / 1e6)

                for i in range(1, 8):
                    addition = int(future_time // 5)
                    if addition == 0:
                        addition = 1
                    for j in range(0, check):
                        if kind_pv_arr[i - 1] == "1":
                            response += f"{load_py[i - 1][81][60][50][total_seconds]}," 
                            # response += "0,"



                response = response[:-1]  # 마지막 콤마 제거  
                # response가 빈 문자열일 경우 처리
                if len(response) == 0:
                    print("--->8082 response is empty.")
                    response = "No valid data available."  # 기본 값을 설정하거나 다른 처리
                else:
                    print(f"--->8082 response: {response}")

                client_socket.send(response.encode('utf-8'))
            
            elif port == 8083:
                print(f"Server {server_id}  8083 received: {message}")
                # 8083 KI0000000TN00:00:17.765AX000

                #AX 추출

                # 내꺼
                message = message[:-1]
                KI_str, TI_str, AX_str= [segment for segment in re.split(r'[a-zA-Z]', message) if segment]
                # print('8083', KI_str, TI_str, AX_str)
                kind_select_index = 0 
                for i in range(len(KI_str)):
                    if KI_str[i] == '1':
                        kind_select_index = i
                        break
                
                ax_index = 0
                for i in range(len(AX_str)):
                    if AX_str[i] == '1':
                        ax_index = i
                        break

                # co, co2, o2, Fuel, 속도(Velocity), 불, 온도
                # co2, o2, co, 온도, 속도, 불, Fuel
                # 
                # print('LO_str: ', list(map(int, LO_str.split(','))))
                kind_index = [1, 2, 0, 6, 4, 5, 3]

                time_split = TI_str.split(':')
                time = float(time_split[0]) * 3600 + float(time_split[1]) * 60 + float(time_split[2])
                # print('8083 parameter: ', kind_select_index, time, ax_index)
                # with lock: # mutex lock 추가
                response = get_8083_ready_data(load_py, kind_index[kind_select_index], time, ax_index)
                

                # 재윤이꺼
                # if ax_index != -1:
                #     selectedXYZ = 3
                #     ax_values = message[ax_index + 2:ax_index + 5]
                #     for i, char in enumerate(ax_values):
                #         if char == '1':
                #             selectedXYZ = i
                #             break 
                #     # x 일 때
                #     if selectedXYZ == 0:
                #         response = f"{resized_Port8083x}"
                #     # y 일 때
                #     elif selectedXYZ == 1:
                #         response = f"{resized_Port8083y}"
                #     # z 일 때
                #     elif selectedXYZ == 2:
                #         if check:  # Corrected check handling
                #             response = f"{resized_Port8083z}"
                #             check = False
                #         else:
                #             response = f"{resized_Port8083_two}"
                #             check = True
                # response = f"Server {server_id} acknowledges: {message}"
                # response = ""
                # print(f"8083 response: {response}")
                # response = ''
                client_socket.send(response.encode('utf-8'))
        except ConnectionResetError:
            break

    client_socket.close()

def start_server(port, server_id):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"Server {server_id} listening on port {port}...")

    while True:
        client_socket, addr = server.accept()
        print(f"Server {server_id} connected with {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, server_id, port))
        client_handler.start()

if __name__ == "__main__":
    ports = [8081, 8082, 8083]
    for i, port in enumerate(ports):
        server_thread = threading.Thread(target=start_server, args=(port, i+1))
        server_thread.start()


# --- 원본 --- 
# import socket
# import threading
# import numpy as np
# import cv2
# from datetime import datetime

# print("Load and print the numpy file")
# load_py = np.load('D:/UnrealData/slicing_sample_data500.npy')

# time = -1
# kind = 1
# #PV port 8081
# flattened_array = load_py[kind, :, :, :, time]


# #port 8081
# x, y, z = 10, 10, 10
# re_flattened_array = flattened_array[x:x+10, y:y+10, z:z+5].reshape(-1)

# #port 8082
# temp = np.rot90(flattened_array, 1, axes=(0,2))
# Port8082z = temp.max(axis=0).reshape(-1)
# Port8082y = temp.max(axis=1).reshape(-1)
# Port8082x = temp.max(axis=2).reshape(-1)


# #port 8083
# flattened_array_two = load_py[kind, :, :, :, -400]
# selectXYZ = 1

# temp = np.rot90(flattened_array, 1, axes=(0,2))
# temp_two = np.rot90(flattened_array_two, 1, axes=(0,2))

# # Port8082z = temp.max(axis=0).reshape(-1)
# # Port8082y = temp.max(axis=1).reshape(-1)
# # Port8082x = temp.max(axis=2).reshape(-1)

# #temp = np.rot90(flattened_array, 1, axes=(0,2))


# #port 8083 100x100 resize 필요.
# Port8083z = temp.max(axis=0)
# Port8083z_two = temp_two.max(axis=0)
# Port8083y = temp.max(axis=1)
# Port8083x = temp.max(axis=2)


# resized_Port8083x = cv2.resize(Port8083x, (100, 100), interpolation=cv2.INTER_LINEAR)
# resized_Port8083y = cv2.resize(Port8083y, (100, 100), interpolation=cv2.INTER_LINEAR)
# resized_Port8083z = cv2.resize(Port8083z, (100, 100), interpolation=cv2.INTER_LINEAR)
# resized_Port8083_two =  cv2.resize(Port8083z_two, (100, 100), interpolation=cv2.INTER_LINEAR)
# # resized_Port8083z = cv2.resize(Port8083z, (100, 100), interpolation=cv2.INTER_LINEAR)
# # resized_Port8083_two =  cv2.resize(Port8083z_two, (100, 100), interpolation=cv2.INTER_LINEAR)

# resized_Port8083x = resized_Port8083x.reshape(-1)
# resized_Port8083y = resized_Port8083y.reshape(-1)
# resized_Port8083z = resized_Port8083z.reshape(-1)
# resized_Port8083_two = resized_Port8083_two.reshape(-1)

# # parshing port 8081
# formatted_string = ",".join(map(str, re_flattened_array))
# # parshing port 8083
# resized_Port8083x = ",".join(map(str, resized_Port8083x))
# resized_Port8083y = ",".join(map(str, resized_Port8083y))
# resized_Port8083z = ",".join(map(str, resized_Port8083z))
# resized_Port8083_two = ",".join(map(str, resized_Port8083_two))
# print(formatted_string)

# check = True

# def handle_client(client_socket, server_id, port):
#     global check
#     while True:
#         try:
#             message = client_socket.recv(3000).decode('utf-8')
#             if not message:
#                 print(f"Server {server_id}  8083 received: break")
#                 break
#             if port == 8081: # 완성
#                 print(f"Server {server_id} 8081 received: {message}")
#                 print(message)
#                 parshing = "PV" + formatted_string
#                 #print("parshing " + parshing)
#                 client_socket.send(parshing.encode('utf-8'))
#             elif port == 8082:
#                 print(f"Server {server_id} 8082 acknowledges: {message}")
#                 KIND_PV_LENGTH = 7
#                 # 'KI' 위치 찾기
#                 message_idx = message.find('KI')

#                 # 초기 변수 선언
#                 kind_pv_arr = []
#                 location_xyz = []
#                 now_time_str = ""
#                 future_time_str = ""

#                 # 'KI'가 있는지 확인
#                 if message_idx != -1:
#                     # 구독된 Kind PV를 담음
#                     kind_pv_arr = message[(message_idx + 2):(message_idx + 2 + KIND_PV_LENGTH - 1)]
#                     print("kind_pv_arr : ", kind_pv_arr )
#                     message_idx += 2 + KIND_PV_LENGTH

#                     # 'TN' 위치 찾기
#                     end_idx = message.find('TN')

#                     # TN이 존재할 경우
#                     if end_idx != -1:
#                         message_idx += 2
#                         # 사용자의 위치가 담긴 location 배열
#                         location_xyz_str = message[message_idx:end_idx - 1].split(',')
#                         location_xyz_str = np.array(location_xyz_str, dtype=float)
#                         location_xyz = np.floor(location_xyz_str)
                        
#                         # TN 이후 부분에서 시간 정보 찾기
#                         message_idx = end_idx + 2
#                         for i in range(message_idx, len(message)):
#                             if message[i] != 'T':
#                                 end_idx = i
#                             else:
#                                 break
                        
#                         # 시간 정보 문자열을 추출
#                         now_time_str = message[message_idx:end_idx]
#                         if end_idx != len(message):
#                             future_time_str = message[end_idx+3:]           
                
#                 # 배열길이 초과를 방지하기 위해 (테스트)
#                 x = location_xyz[0]
#                 y = location_xyz[1]
#                 z = location_xyz[2]
#                 k = now_time_str
                
#                 parsed_time = datetime.strptime(k, "%H:%M:%S.%f")
#                 # 초 단위로 변환
#                 total_seconds = int(parsed_time.hour * 3600 + parsed_time.minute * 60 + parsed_time.second + parsed_time.microsecond / 1e6)

#                 # try:
#                 #     k_value = float(k.split(":")[-1])  # 예를 들어, "00:00:01.324"에서 1.324를 추출
#                 # except ValueError:
#                 #     # 문자열이 예상과 다를 경우 에러 핸들링
#                 #     k_value = 0.0

                
#                 if(x >= load_py.shape[1]):
#                     x = load_py.shape[1]
                    
#                 if(y >= load_py.shape[2]):
#                     y = load_py.shape[2]

#                 if(z >= load_py.shape[3]):
#                     z = load_py.shape[3]
#                 if total_seconds >= load_py.shape[4]:
#                     total_seconds = load_py.shape[4] 
#                 # if(k. >= load_py.shape[4]):
#                 #     k = load_py.shape[4]-1
                
#                 # 요청한 현재 시간의 정보를 response추가
#                 response = ""  # 혹은 response = []로 리스트로 초기화
#                 for i in range(len(kind_pv_arr)):
#                     if kind_pv_arr[i] == "1":  # i는 인덱스
#                         response += f"{load_py[i][x][y][z][total_seconds]},"
#                 future_time_str = future_time_str.replace('\x00', '')  # 널 문자를 제
#                 if(int(future_time_str) == 0):
#                     response = response[:-1]  # pop() 대신 슬라이싱 사용
#                 else:

#                     for i in range(1, int(future_time_str)/10):
#                         if (total_seconds+i) > load_py.shape[4]:
#                             total_seconds = load_py.shape[4]
#                         else:
#                             total_seconds += i
                            
#                         response += f"{load_py[kind_pv_arr[i]][x][y][z][total_seconds]},"
                
#                     response = response[:-1]  # pop() 대신 슬라이싱 사용
#                 #response
#                 print(f"--->8082 response: f{response}")
#                 client_socket.send(response.encode('utf-8'))
            
#             elif port == 8083:
#                 print(f"Server {server_id}  8083 received: {message}")
#                 print(message)

#                 #AX 추출
#                 ax_index = message.find("AX")
#                 response = "Invalid request"  # 기본값으로 초기화
#                 if ax_index != -1:
#                     selectedXYZ = 3
#                     ax_values = message[ax_index + 2:ax_index + 5]
#                     for i, char in enumerate(ax_values):
#                         if char == '1':
#                             selectedXYZ = i
#                             break 
#                     # x 일 때
#                     if selectedXYZ == 0:
#                         response = f"{resized_Port8083x}"
#                     # y 일 때
#                     elif selectedXYZ == 1:
#                         response = f"{resized_Port8083y}"
#                     # z 일 때
#                     elif selectedXYZ == 2:
#                         if check:  # Corrected check handling
#                             response = f"{resized_Port8083z}"
#                             check = False
#                         else:
#                             response = f"{resized_Port8083_two}"
#                             check = True
#                 # response = f"Server {server_id} acknowledges: {message}"
#                 client_socket.send(response.encode('utf-8'))
#         except ConnectionResetError:
#             break

#     client_socket.close()

# def start_server(port, server_id):
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind(('0.0.0.0', port))
#     server.listen(5)
#     print(f"Server {server_id} listening on port {port}...")

#     while True:
#         client_socket, addr = server.accept()
#         print(f"Server {server_id} connected with {addr}")
#         client_handler = threading.Thread(target=handle_client, args=(client_socket, server_id, port))
#         client_handler.start()

# if __name__ == "__main__":
#     ports = [8081, 8082, 8083]
#     for i, port in enumerate(ports):
#         server_thread = threading.Thread(target=start_server, args=(port, i+1))
#         server_thread.start()
