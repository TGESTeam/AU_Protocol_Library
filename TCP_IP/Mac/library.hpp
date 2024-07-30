#ifndef LIBRARY_HPP
#define LIBRARY_HPP

#include <iostream>
#include <string>

using namespace std;

//---Shape(3D 데이터) 파싱---

//동적 할당 해제
void deallocate_3d_array(double*** array, int x_dim, int y_dim) {
    for (int i = 0; i < x_dim; ++i) {
        for (int j = 0; j < y_dim; ++j) {
            delete[] array[i][j];
        }
        delete[] array[i];
    }
    delete[] array;
}

//동적 할당
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

//3D 데이터 파싱
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



#endif