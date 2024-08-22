import socket
import threading

def handle_client(client_socket, server_id):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Server {server_id} received: {message}")
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
        client_handler = threading.Thread(target=handle_client, args=(client_socket, server_id))
        client_handler.start()

if __name__ == "__main__":
    ports = [8081, 8082, 8083]
    for i, port in enumerate(ports):
        server_thread = threading.Thread(target=start_server, args=(port, i+1))
        server_thread.start()
