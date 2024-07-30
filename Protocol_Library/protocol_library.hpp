#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <sstream>  // 이 부분을 추가합니다.

#include <cstdlib>
#include <unistd.h> // getpid() 함수 사용을 위해 필요

using namespace std;

//Enum
enum SeperatorEnum {
	LO, RO, VL, TI, SH, PV
};

struct request{

};

struct response{
    vector<long> shape_size;

};


//-------- c++ -> python -----------

//---Shape(3D 데이터) 파싱---

//3차원 동적 할당 해제
void deallocate_3d_array(double*** array, int x_dim, int y_dim) {
    for (int i = 0; i < x_dim; ++i) {
        for (int j = 0; j < y_dim; ++j) {
            delete[] array[i][j];
        }
        delete[] array[i];
    }
    delete[] array;
}

//3차원 동적 할당
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

//--------python -> c++-----------

//SH -> shape size 들고오기
void shape_parsing(response *res, string &str){
    long num;
    long i = 2;
    long j;
    int idx = 0;
    long resut;
 
    while (1)
    {
        num = 0;
        while (str[i] >= '0' && str[i] <= '9')
        {
            num = num * 10 + (str[i] - '0');
            i++;
        }
        res->shape_size.push_back(num);
        if (str[i] == 'P')
            break;
        i++;
    }
    // str의 i번째부터 끝까지 부분 문자열로 바꾸기
    str = str.substr(i);
}

//str의 4차원 값 -> 4차원 배열 파싱
void parse_and_fill_array(double ****arr, const std::vector<long>& shape_size, const std::string& str) 
{
    istringstream ss(str.substr(3)); // 'PV '를 건너뛰고 시작
    string token;
    vector<double> values;

    // 쉼표로 구분된 숫자들을 추출
    while (getline(ss, token, ',')) {
        values.push_back(stod(token));
    }

    // 값을 4차원 배열에 채우기
    int index = 0;
    for (int i = 0; i < shape_size[0]; ++i) {
        for (int j = 0; j < shape_size[1]; ++j) {
            for (int k = 0; k < shape_size[2]; ++k) {
                for (int l = 0; l < shape_size[3]; ++l) {
                    if (index < values.size()) {
                        arr[i][j][k][l] = values[index++];
                    } else {
                        std::cerr << "Error: Not enough values provided in the string." << std::endl;
                        return;
                    }
                }
            }
        }
    }
}


//4차원 동적 할당 해제
void deallocate_4d_array(double**** data, int x, int y, int z) {
    for (int i = 0; i < x; i++) {
        for (int j = 0; j < y; j++) {
            for (int k = 0; k < z; k++) {
                delete[] data[i][j][k];
            }
            delete[] data[i][j];
        }
        delete[] data[i];
    }
    delete[] data;
}



//4차원 동적 할당
double ****allocate_4d_array(int x, int y, int z, int w) {
    double**** data = new double***[x];
    for (int i = 0; i < x; i++) {
        data[i] = new double**[y];
        for (int j = 0; j < y; j++) {
            data[i][j] = new double*[z];
            for (int k = 0; k < z; k++) {
                data[i][j][k] = new double[w];
            }
        }
    }
    return data;
}


// 4차원 배열 출력 함수
void print_4d_array(double ****arr, const std::vector<long>& shape_size) {
    for (int i = 0; i < shape_size[0]; ++i) {
        for (int j = 0; j < shape_size[1]; ++j) {
            for (int k = 0; k < shape_size[2]; ++k) {
                for (int l = 0; l < shape_size[3]; ++l) {
                    std::cout << "arr[" << i << "][" << j << "][" << k << "][" << l << "] = " << arr[i][j][k][l] << std::endl;
                }
            }
        }
    }
}

