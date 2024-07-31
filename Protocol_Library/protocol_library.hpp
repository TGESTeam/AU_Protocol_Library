#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <sstream> // 이 부분을 추가합니다.

#include <cstdlib>
#include <unistd.h> // getpid() 함수 사용을 위해 필요

using namespace std;

const char NEXT_OF_SHAPE = 'P';
// const char * NEXT_OF_SHAPE = "PV"; // array로 하면 더 직관적일까?

// Enum
enum SeperatorEnum
{ // 0~6
    LO,
    RO,
    VL,
    TI,
    SH,
    PV
};

struct request
{
};

// struct response{
//  Python에 전송할때도 필요해서 이름 수정함
struct arrayShape
{
    vector<long> shape_size;
};

/* --------[실제 코드쓸때는 삭제 해야함]---------- */
struct FVector
{
    double X;
    double Y;
    double Z;
};

struct FRotation
{
    double Pitch;
    double Yaw;
    double Roll;
};
/* ------------------ */

//-------- c++ <-- python -----------

//---Shape(3D 데이터) 파싱---

// 3차원 동적 할당 해제
void deallocate_3d_array(double ***array, int x_dim, int y_dim)
{
    for (int i = 0; i < x_dim; ++i)
    {
        for (int j = 0; j < y_dim; ++j)
        {
            delete[] array[i][j];
        }
        delete[] array[i];
    }
    delete[] array;
}

// 3차원 동적 할당
double ***allocate_3d_array(int x, int y, int z)
{
    double ***data = new double **[x];
    for (int i = 0; i < x; i++)
    {
        data[i] = new double *[y];
        for (int j = 0; j < y; j++)
        {
            data[i][j] = new double[y];
        }
    }
    return data;
}

// 3D 데이터 파싱
string pashing_3D(double ***data, int x, int y, int z)
{
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

// SH -> shape size 들고오기
void shape_parsing(arrayShape *res, string &str)
{
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
            cout << (i - 1) << "번째:" << num << endl;
        }
        res->shape_size.push_back(num);
        if (str[i] == NEXT_OF_SHAPE)
            break;
        i++;
    }
    // str의 i번째부터 끝까지 부분 문자열로 바꾸기
    str = str.substr(i);
}

// str의 4차원 값 -> 4차원 배열 파싱
void parse_and_fill_array(double ****arr, const std::vector<long> &shape_size, const std::string &str)
{
    istringstream ss(str.substr(3)); // 'PV '를 건너뛰고 시작
    string token;
    vector<double> values;

    // 쉼표로 구분된 숫자들을 추출
    while (getline(ss, token, ','))
    {
        values.push_back(stod(token));
    }

    // 값을 4차원 배열에 채우기
    int index = 0;
    for (int i = 0; i < shape_size[0]; ++i)
    {
        for (int j = 0; j < shape_size[1]; ++j)
        {
            for (int k = 0; k < shape_size[2]; ++k)
            {
                for (int l = 0; l < shape_size[3]; ++l)
                {
                    if (index < values.size())
                    {
                        arr[i][j][k][l] = values[index++];
                    }
                    else
                    {
                        std::cerr << "Error: Not enough values provided in the string." << std::endl;
                        return;
                    }
                }
            }
        }
    }
}

// 4차원 동적 할당 해제
void deallocate_4d_array(double ****data, int x, int y, int z)
{
    for (int i = 0; i < x; i++)
    {
        for (int j = 0; j < y; j++)
        {
            for (int k = 0; k < z; k++)
            {
                delete[] data[i][j][k];
            }
            delete[] data[i][j];
        }
        delete[] data[i];
    }
    delete[] data;
}

// 4차원 동적 할당
double ****allocate_4d_array(int x, int y, int z, int w)
{
    double ****data = new double ***[x];
    for (int i = 0; i < x; i++)
    {
        data[i] = new double **[y];
        for (int j = 0; j < y; j++)
        {
            data[i][j] = new double *[z];
            for (int k = 0; k < z; k++)
            {
                data[i][j][k] = new double[w];
            }
        }
    }
    return data;
}

// 4차원 배열 출력 함수
void print_4d_array(double ****arr, const std::vector<long> &shape_size)
{
    cout.precision(16);
    cout << "----------------[print_4d_array start]----------------" << endl;
    for (int i = 0; i < shape_size[0]; ++i)
    {
        for (int j = 0; j < shape_size[1]; ++j)
        {
            for (int k = 0; k < shape_size[2]; ++k)
            {
                for (int l = 0; l < shape_size[3]; ++l)
                {
                    std::cout << "arr[" << i << "][" << j << "][" << k << "][" << l << "] = " << arr[i][j][k][l] << std::endl;
                }
            }
        }
    }

    cout << "----------------[print_4d_array end]----------------" << endl
         << endl;
}

// -------------- cpp -> python -----------------

// 인코딩할 문자열 계산(4개의 Separator)
// 배열길이, 사용자의 위치, 사용자의 방향, 4차원 데이터
string::size_type cal_new_string_capacity(const vector<long> &shape_size, const FVector &playerLocation, const FRotation &playerRotation)
{
    /*
        0. (Separator갯수*2)를 더한다.
        1. n차원일 때 n값을 더한다. (콤마는 해당 길이만큼 들어가기에)
        2. (n-1)을 더한다.
        3. 배열길이를 계산한다.
        4. (배열길이-1) 만큼 수를 더한다.
        5. (vector의 갯수*3) 만큼 수를 더한다. (Vector는 FVector, FRotation등을 의미)
        6. (위의 수-1)만큼 수를 더한다.
    */
    const int separatorNum = 4;                                                            // separator 종류
    const int shapeLength = 4;                                                             // 차원의 종류(2차원이면 값이 2)
    const int arrayLength = shape_size[0] * shape_size[1] * shape_size[2] * shape_size[3]; // 배열길이
    const int playerVectorNum = 2;
    const int maxLengthOfDouble = 16; //double이 최대 15+1(음수)자리 숫자를 가진다... 그러니 이를 체크                                                  // player의 위치, 방향등에 대한 벡터의 갯수

    // 같은 변수끼리 ()를 더 묶음
    return (separatorNum * 2)
           +((shapeLength*maxLengthOfDouble) + (shapeLength - 1)) 
           +((arrayLength*maxLengthOfDouble) + (arrayLength - 1))
           +((playerVectorNum*maxLengthOfDouble * 3) + ((playerVectorNum * 3) - 1));
}

void encoding_to_SH(const vector<long> &shape_size, string &encodedStr)
{
    encodedStr.append("SH"); // separator 설정

    if (shape_size.size() == 0)
    {
        cout << "shape_size's size is 0!" << endl;
        return;
    }

    for (int i = 0; i < shape_size.size(); i++)
    {
        encodedStr.append(to_string(shape_size[i]));
        if (i == (shape_size.size()-1))
        {
            continue;
        }

        encodedStr.append(",");
    }
}

void encoding_to_LO(const FVector &playerLocation, string &encodedStr)
{
    encodedStr.append("LO"); // separator 설정

    encodedStr.append(to_string(playerLocation.X));
    encodedStr.append(",");
    encodedStr.append(to_string(playerLocation.Y));
    encodedStr.append(",");
    encodedStr.append(to_string(playerLocation.Z));
}

void encoding_to_RO(const FRotation &playerRotation, string &encodedStr)
{
    encodedStr.append("LO"); // separator 설정

    encodedStr.append(to_string(playerRotation.Pitch));
    encodedStr.append(",");
    encodedStr.append(to_string(playerRotation.Roll));
    encodedStr.append(",");
    encodedStr.append(to_string(playerRotation.Yaw));
}

// 4차원 공간 데이터를 encoding한다
void encoding_to_VL(double ****spatialDataArr, const vector<long> &shape_size, string &encodedStr)
{
    encodedStr.append("VL");
    int endCheck = 0; // 배열의 끝을 체크하는 변수
    int array_volume = (shape_size[0]*shape_size[1]*shape_size[2]*shape_size[3]); // 4차원 배열의 넓이

    for (int i = 0; i < shape_size[0]; ++i)
    {
        for (int j = 0; j < shape_size[1]; ++j)
        {
            for (int k = 0; k < shape_size[2]; ++k)
            {
                for (int l = 0; l < shape_size[3]; ++l)
                {
                    encodedStr.append(to_string(spatialDataArr[i][j][k][l]));
                    if ((++endCheck) < (array_volume))
                    { // 마지막 배열아 아닐 때
                        encodedStr.append(",");
                    }
                }
            }
        }
    }
}

// 4차원, 2개의 데이터를을 str로 만들기
void three_separator_encoding(double ****spatialDataArr, const vector<long> &shape_size, const FVector &playerLocation, const FRotation &playerRotation, string &encodedStr)
{
    //  5-1. 문자열의 공간을 미리 계산 후, reserve로 계산된만큼 할당
    //int capaciy_check = ;
    //cout << capaciy_check << endl;
    encodedStr.reserve(cal_new_string_capacity(shape_size, playerLocation, playerRotation));
    cout<<"------> copacity(before input):" << encodedStr.capacity()<<endl;

    if (spatialDataArr == nullptr)
    {
        cout << "spatialDataArr is null" << endl;
        return;
    }

    encoding_to_SH(shape_size, encodedStr);
    encoding_to_LO(playerLocation, encodedStr);
    encoding_to_RO(playerRotation, encodedStr);
    encoding_to_VL(spatialDataArr, shape_size, encodedStr);

    cout<<"------> copacity(after input):" << encodedStr.capacity()<<endl;
    cout<<"------> size(after input):"<<encodedStr.size()<<endl;
    return;
}