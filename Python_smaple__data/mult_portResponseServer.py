import socket
import threading
import numpy as np
import cv2

print("Load and print the numpy file")
load_py = np.load('D:/UnrealData/slicing_sample_data500.npy')

time = -1
kind = 1
#PV port 8081
flattened_array = load_py[kind, :, :, :, time]


#port 8081
x, y, z = 10, 10, 10
re_flattened_array = flattened_array[x:x+10, y:y+10, z:z+5].reshape(-1)

#port 8082
temp = np.rot90(flattened_array, 1, axes=(0,2))
Port8082z = temp.max(axis=0).reshape(-1)
Port8082y = temp.max(axis=1).reshape(-1)
Port8082x = temp.max(axis=2).reshape(-1)


#port 8083
flattened_array_two = load_py[kind, :, :, :, -400]
selectXYZ = 1

temp = np.rot90(flattened_array, 1, axes=(0,2))
temp_two = np.rot90(flattened_array_two, 1, axes=(0,2))

# Port8082z = temp.max(axis=0).reshape(-1)
# Port8082y = temp.max(axis=1).reshape(-1)
# Port8082x = temp.max(axis=2).reshape(-1)

#temp = np.rot90(flattened_array, 1, axes=(0,2))


#port 8083 100x100 resize 필요.
Port8083z = temp.max(axis=0)
Port8083z_two = temp_two.max(axis=0)
Port8083y = temp.max(axis=1)
Port8083x = temp.max(axis=2)


resized_Port8083x = cv2.resize(Port8083x, (100, 100), interpolation=cv2.INTER_LINEAR)
resized_Port8083y = cv2.resize(Port8083y, (100, 100), interpolation=cv2.INTER_LINEAR)
resized_Port8083z = cv2.resize(Port8083z, (100, 100), interpolation=cv2.INTER_LINEAR)
resized_Port8083_two =  cv2.resize(Port8083z_two, (100, 100), interpolation=cv2.INTER_LINEAR)
# resized_Port8083z = cv2.resize(Port8083z, (100, 100), interpolation=cv2.INTER_LINEAR)
# resized_Port8083_two =  cv2.resize(Port8083z_two, (100, 100), interpolation=cv2.INTER_LINEAR)

resized_Port8083x = resized_Port8083x.reshape(-1)
resized_Port8083y = resized_Port8083y.reshape(-1)
resized_Port8083z = resized_Port8083z.reshape(-1)
resized_Port8083_two = resized_Port8083_two.reshape(-1)

# parshing port 8081
formatted_string = ",".join(map(str, re_flattened_array))
# parshing port 8083
resized_Port8083x = ",".join(map(str, resized_Port8083x))
resized_Port8083y = ",".join(map(str, resized_Port8083y))
resized_Port8083z = ",".join(map(str, resized_Port8083z))
resized_Port8083_two = ",".join(map(str, resized_Port8083_two))
print(formatted_string)

check = True

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
                print(message)
                parshing = "PV" + formatted_string
                #print("parshing " + parshing)
                client_socket.send(parshing.encode('utf-8'))
            elif port == 8082:
                print(f"Server {server_id} 8082 acknowledges: {message}")
                KIND_PV_LENGTH = 7;
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
                    kind_pv_arr = message[(message_idx + 2):(message_idx + 2 + KIND_PV_LENGTH - 1)]
                    message_idx += 2 + KIND_PV_LENGTH

                    # 'TN' 위치 찾기
                    end_idx = message.find('TN')

                    # TN이 존재할 경우
                    if end_idx != -1:
                        message_idx += 2
                        # 사용자의 위치가 담긴 location 배열
                        location_xyz_str = message[message_idx:end_idx].split(',')
                        
                        location_xyz_str = np.array(location_xyz_str, dtype=float)
                        location_xyz = np.floor(location_xyz_str)
                        
                        # TN 이후 부분에서 시간 정보 찾기
                        message_idx = end_idx + 2
                        for i in range(message_idx, len(message)):
                            if message[i] != 'T':
                                end_idx = i
                            else:
                                break
                        
                        # 시간 정보 문자열을 추출
                        now_time_str = message[message_idx:end_idx]
                        if end_idx != len(message):
                            future_time_str = message[end_idx+3:]           
                
                # 배열길이 초과를 방지하기 위해 (테스트)
                x = location_xyz[0]
                y = location_xyz[1]
                z = location_xyz[2]
                k = now_time_str
                
                if(x >= load_py.shape[1]):
                    x = load_py.shape[1]-1
                    
                if(y >= load_py.shpae[2]):
                    y = load_py.shpae[2]-1
                
                if(z >= load_py.shape[3]):
                    z = load_py.shape[3]-1
                    
                if(k >= load_py.shape[4]):
                    k = load_py.shape[4]-1;
                
                # 요청한 현재 시간의 정보를 response추가
                for i in kind_pv_arr:
                    if(kind_pv_arr[i] == 1):
                        response += f"{load_py[kind_pv_arr[i]][x][y][z][k]},"
                
                if(future_time_str == 0):
                    response.pop()
                
                else:
                    for i in range(1, future_time_str/10):
                        if (k+i) > load_py.shape[4]:
                            k = load_py.shape[4]
                        else:
                            k += i
                            
                        response += f"{load_py[kind_pv_arr[i]][x][y][z][k]},"
                
                    response .pop()
                #response
                print(f"--->8082 response: f{response}")
                client_socket.send(response.encode('utf-8'))
            
            elif port == 8083:
                print(f"Server {server_id}  8083 received: {message}")
                print(message)

                #AX 추출
                ax_index = message.find("AX")
                response = "Invalid request"  # 기본값으로 초기화
                if ax_index != -1:
                    selectedXYZ = 3
                    ax_values = message[ax_index + 2:ax_index + 5]
                    for i, char in enumerate(ax_values):
                        if char == '1':
                            selectedXYZ = i
                            break 
                    # x 일 때
                    if selectedXYZ == 0:
                        response = f"{resized_Port8083x}"
                    # y 일 때
                    elif selectedXYZ == 1:
                        response = f"{resized_Port8083y}"
                    # z 일 때
                    elif selectedXYZ == 2:
                        if check:  # Corrected check handling
                            response = f"{resized_Port8083z}"
                            check = False
                        else:
                            response = f"{resized_Port8083_two}"
                            check = True
                # response = f"Server {server_id} acknowledges: {message}"
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
