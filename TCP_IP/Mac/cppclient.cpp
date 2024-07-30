#include <iostream>
#include <string>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <string>

using namespace std;

#define SERVER_HOST "127.0.0.1"
#define SERVER_PORT 8080
#define BUFFER_SIZE 1024

string pashing_3D(double ***data, int x, int y, int z){
    string str;

    str = to_string(x) + "," + to_string(y) + "," + to_string(z) + "$";
    for (int i = 0; i < x; i++)
    {
        for (int j = 0; j < y; j++)
        {
            for (int k = 0; k < z; k++)
            {
                str += to_string(data[i][j][k]);
                if (!(i == x - 1 && j == y - 1 && k == z - 1))
                    str += ",";
            }
        }
        
    }

    return str;
}

double ***allocate_3d_array(int x, int y, int z){
    double*** data = new double**[x];
    for (int i = 0; i < x; i++)
    {
        data[i] = new double*[y];
        for (int j = 0; j < y; j++)
        {
            data[i][j] = new double[y];
        }
    }
    return data;
}

void deallocate_3d_array(double*** array, int x_dim, int y_dim) {
    for (int i = 0; i < x_dim; ++i) {
        for (int j = 0; j < y_dim; ++j) {
            delete[] array[i][j];
        }
        delete[] array[i];
    }
    delete[] array;
}

void send_3d_data(int sock) {

    //3차원 배열 난수 생성
    int x = 5;
    int y = 5;
    int z = 5;

    double ***data = allocate_3d_array(x, y, z);
    srand(static_cast<unsigned>(time(0)));

    // 배열에 난수 채우기 (소수)
    for (int i = 0; i < x; ++i) {
        for (int j = 0; j < y; ++j) {
            for (int k = 0; k < z; ++k) {
                data[i][j][k] = static_cast<double>(rand()) / RAND_MAX;       
            }
        }
    }

    string send_data = pashing_3D(data, x, y ,z);

    // 결과 출력
    cout << send_data << endl;

    
    send(sock, send_data.c_str(), send_data.size(), 0);

    // 동적 배열 해제
    deallocate_3d_array(data, x, y);
    

    char buffer[BUFFER_SIZE] = {0};
    int valread = read(sock, buffer, BUFFER_SIZE);
    if (valread > 0) {
        std::cout << "Received from server: " << std::string(buffer, valread) << std::endl;
    }
}

int main() 
{
    int sock = 0;
    struct sockaddr_in serv_addr;
    char buffer[BUFFER_SIZE] = {0};

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cout << "Socket creation error." << std::endl;
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(SERVER_PORT);

    if (inet_pton(AF_INET, SERVER_HOST, &serv_addr.sin_addr) <= 0) {
        std::cout << "Invalid address/ Address not supported." << std::endl;
        return -1;
    }

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cout << "Connection Failed." << std::endl;
        return -1;
    }

    std::string message;
    while (true) {
        std::cout << "Enter message to send to server (type 'exit' to quit, type 'send3d' to send 3D data): ";
        std::getline(std::cin, message);
        if (message == "exit") {
            break;
        } else if (message == "send3d") {
            send_3d_data(sock);
            continue;
        }

        send(sock, message.c_str(), message.size(), 0);
        int valread = read(sock, buffer, BUFFER_SIZE);
        if (valread > 0) {
            std::cout << "Received from server: " << std::string(buffer, valread) << std::endl;
        }
    }

    close(sock);
    return 0;
}
