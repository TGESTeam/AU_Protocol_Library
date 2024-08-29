import socket
import threading
import numpy as np

print("Load and print the numpy file")
load_py = np.load('D:/UnrealData/slicing_sample_data.npy')
flattened_array = load_py[6, :, :, :, 0].reshape(-1)[:60]
formatted_string = ",".join(map(str, flattened_array))
print(formatted_string)

def handle_client(client_socket, server_id, port):
    while True:
        try:
            message = client_socket.recv(3000).decode('utf-8')
            if not message:
                break
            if port == 8081:
                print(f"Server {server_id} received: {message}")
                print(message)
                parshing = "PV" + formatted_string
                client_socket.send(parshing.encode('utf-8'))
            elif port == 8082:
                print(f"Server {server_id} received: {message}")
                print(message)
                response = f"Server {server_id} acknowledges: {message}"
                client_socket.send(response.encode('utf-8'))
            elif port == 8083:
                print(f"Server {server_id} received: {message}")
                print(message)
                response = f"Server {server_id} acknowledges: {message}"
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
