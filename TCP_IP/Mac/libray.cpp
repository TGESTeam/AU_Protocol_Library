#include <iostream>
#include <string>

using namespace std;

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


int main()
{
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

    // 동적 배열 해제
    deallocate_3d_array(data, x, y);


    
}