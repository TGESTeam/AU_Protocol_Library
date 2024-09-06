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


#port 8083
selectXYZ = 1
temp = np.rot90(flattened_array, 1, axes=(0,2))

# Port8082z = temp.max(axis=0).reshape(-1)
# Port8082y = temp.max(axis=1).reshape(-1)
# Port8082x = temp.max(axis=2).reshape(-1)

#port 8083 100x100 resize 필요.
Port8083z = temp.max(axis=0)
Port8083y = temp.max(axis=1)
Port8083x = temp.max(axis=2)

resized_Port8083x = cv2.resize(Port8083x, (100, 100), interpolation=cv2.INTER_LINEAR)
resized_Port8083y = cv2.resize(Port8083y, (100, 100), interpolation=cv2.INTER_LINEAR)
resized_Port8083z = cv2.resize(Port8083z, (100, 100), interpolation=cv2.INTER_LINEAR)

resized_Port8083x = resized_Port8083x.reshape(-1)
resized_Port8083y = resized_Port8083y.reshape(-1)
resized_Port8083z = resized_Port8083z.reshape(-1)

# parshing port 8081
formatted_string = ",".join(map(str, re_flattened_array))
# parshing port 8083
resized_Port8083x = ",".join(map(str, resized_Port8083x))
resized_Port8083y = ",".join(map(str, resized_Port8083y))
resized_Port8083z = ",".join(map(str, resized_Port8083z))
print(formatted_string)

def handle_client(client_socket, server_id, port):
    while True:
        try:
            message = client_socket.recv(3000).decode('utf-8')
            if not message:
                break
            if port == 8081: # 완성
                print(f"Server {server_id} 8081 received: {message}")
                print(message)
                parshing = "PV" + formatted_string
                #print("parshing " + parshing)
                client_socket.send(parshing.encode('utf-8'))
            elif port == 8082:
                # x,y,z값에 따라 응답값을 주어야함.
                print(f"Server {server_id} 8082 received: {message}")
                print(message)
                response = f"Server {server_id} acknowledges: {message}"
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
                        response = f"{resized_Port8083z}"
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
