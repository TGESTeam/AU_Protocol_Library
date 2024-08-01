#include "protocol_library.hpp"
#include <random>

// void fn() {
//     char cmd[256];
//    snprintf(cmd, sizeof(cmd), "leaks %d", getpid());
//     system(cmd);
// }

void getVolumeLevelData(double ****arr, const vector<long> &shape_size);
void print_SHAPE_LO_RO_VL(double ****spatialDataArr, const vector<long> &shape_size, const FVector &playerLocation, const FRotation &playerRotation);

int main(void)
{
    // ------------- cpp <- python -------------
    // 메모리 누수
    // atexit(fn);

    // c++ -> python
    // 4가지의 데이터를 다 받았어 그리고 난 후 str만들엇다고 가정을 함.
    // string str = "LO12.413,12.42,14.25RO124.414VL23.23,23.24,16.42,54,23,5,4,5$0.880433,0.439875,0.971657,0.637344,0.844048,0.907729,0.204399,0.334862,0.025892,0.171160,0.678607,0.339864,0.098066,0.189742,0.991320,0.110208,0.267243,0.554422,0.162191,0.948080,0.380536,0.671024,0.906936,0.878784,0.730653,0.090425,0.772139,0.345223,0.167508,0.300000,0.106378,0.890144,0.642777,0.153993,0.152022,0.029841,0.536658,0.606858,0.458641,0.381241,0.515843,0.772402,0.753661,0.772813,0.665886,0.552688,0.019633,0.973252,0.445414,0.069739,0.109321,0.351083,0.657066,0.312700,0.541399,0.294261,0.642189,0.278562,0.797876,0.900215,0.920445,0.915183,0.472945,0.778832,0.833128,0.378071,0.237169,0.098905,0.296365,0.014483,0.411988,0.280228,0.795961,0.709670,0.422487,0.731726,0.119132,0.247839,0.431352,0.731654,0.916594,0.203615,0.162386,0.221584,0.165032,0.686718,0.663015,0.300108,0.913682,0.253871,0.801805,0.935707,0.426321,0.179944,0.314657,0.441601,0.981159,0.338236,0.733087,0.998121,0.426212,0.337436,0.293959,0.569833,0.191151,0.676903,0.704564,0.613438,0.057972,0.339685,0.088318,0.360245,0.630590,0.322225,0.634588,0.514931,0.449357,0.338238,0.758226,0.497497,0.430506,0.521660,0.542326,0.866740,0.298458,50TI08:34:23:42";
    //  int i = SeperatorEnum::LO;
    //  if (i ==  SeperatorEnum::LO) {
    //  	cout << "Hello World!!" << endl;
    //  }

    // python -> c++
    // 여기서 buffer 사용
    arrayShape res;
    // response
    string str = "SH2,3,5,5PV-0.960625,0.783478,-0.0856906,-0.201717,-0.256994,0.697063,-0.461489,-0.250461,0.493683,-0.676286,-0.337857,-0.369255,-0.0710619,-0.337391,-0.531616,-0.868504,-0.943532,0.0564975,-0.44627,-0.455976,0.416959,-0.164209,0.136685,-0.72933,0.156272,0.468329,-0.793119,0.0506389,-0.911872,0.168495,-0.110171,0.359727,-0.0622134,0.38017,-0.486012,-0.397147,-0.850608,-0.162731,0.973684,0.704418,-0.842531,-0.420712,-0.899657,-0.533631,-0.728226,0.705206,0.392345,0.134381,0.547705,-0.72424,-0.298193,0.264756,-0.244871,0.460218,0.886352,0.913756,-0.508029,-0.446262,-0.324743,0.0425909,-0.174167,0.782097,0.711707,-0.336091,-0.687546,0.410454,0.492772,0.0186072,0.73133,-0.536444,-0.013349,-0.357064,0.824866,-0.47317,-0.564275,0.232579,0.9509,-0.215677,-0.890762,0.96231,-0.460364,0.659487,-0.00721048,0.813517,0.772494,-0.694496,-0.388403,0.111593,-0.464554,0.238536,-0.923446,-0.359905,-0.918741,0.717855,0.997262,0.982999,-0.731381,-0.325912,0.390625,-0.770967,0.351698,0.982348,0.32737,0.109339,-0.338593,-0.738096,0.81933,0.47778,0.0479915,0.592887,0.64464,0.462764,-0.317997,-0.571538,0.156057,0.851513,-0.614229,0.651882,0.185362,-0.620465,-0.156867,-0.462853,0.828451,-0.226452,0.0166015,-0.979222,0.222536,0.159939,0.0951016,0.372092,-0.252277,-0.027874,-0.477847,0.824855,-0.665135,-0.923142,0.745236,-0.819535,0.0695233,0.478316,-0.948037,0.34586,0.877244,-0.154562,0.27456, 0.52772,-0.612505,-0.37313,0.804608,-0.950896";

    // size 분리
    shape_parsing(&res, str);

    cout << "----------------[str start]----------------" << endl;
    cout << str << endl;
    cout << "----------------[str end]------------------" << endl;
    // 4차원 동적할당
    double ****arr = allocate_4d_array(res.shape_size[0], res.shape_size[1], res.shape_size[2], res.shape_size[3]);

    parse_and_fill_array(arr, res.shape_size, str);
    print_4d_array(arr, res.shape_size);

    // 4차원 동적할당 해제
    deallocate_4d_array(arr, res.shape_size[0], res.shape_size[1], res.shape_size[2]);

    // ------------- cpp -> python -------------
    cout << "------------- cpp -> python -------------" << endl;

    // 1. Array의 공간을 동적으로 할당한다.
    //    배열 길이는 받아올 4차원 데이터가 얼만지 측정했다고 가정함.
    arrayShape shape;
    shape.shape_size = {2, 3, 5, 5};
    double ****spatialDataArr = allocate_4d_array(shape.shape_size[0], shape.shape_size[1], shape.shape_size[2], shape.shape_size[3]); // 배열길이는 임의로

    // 2. 사용자의 위치를 받아온다.
    //    Unreal에서 Location, Rotation을 받았다고 가정함
    FVector playerLocation = {1.111, 2.222, 3.333};   // [LO]: x, y, z
    FRotation playerRotation = {1.111, 2.222, 3.333}; // [RO]: Pitch, Yaw, Roll

    // 3. 4차원 데이터(VL)를 받아온다.
    /* Velocity(3차원)
       Acceleration(3차원) // 가속도
       CO(3차원)
       CO2 (3차원)
       O2 (3차원)
       Fuel (3차원)
       Temperature (3차원)
    */
    getVolumeLevelData(spatialDataArr, shape.shape_size); // 예시를 위한 데이터 넣음

    // 4. 받은 데이터들을 출력한다.
    print_SHAPE_LO_RO_VL(spatialDataArr, shape.shape_size, playerLocation, playerRotation);
    print_4d_array(spatialDataArr, shape.shape_size);

    // 5. 문자열을 만든다.
    //  5-1. 문자열의 공간을 미리 할당해야 한다
    //       (append()를 통해서 새로운 할당의 반복을 막기위해)
    string encodedStr;
    three_separator_encoding(spatialDataArr, shape.shape_size, playerLocation, playerRotation, encodedStr);

    // 6. 문자열을 로그창에 출력한다.
    cout << "----------------[encodingStr start]----------------" << endl;
    cout << encodedStr << endl;
    cout << "----------------[encodingStr end]----------------" << endl << endl;
    return 0;
}

void getVolumeLevelData(double ****arr, const vector<long> &shape_size)
{                                                          // 예시 작성을 위한 랜덤 데이터
    random_device rd;                                      // 하드웨어 기반 난수 생성기
    mt19937 gen(rd());                                     // Mersenne Twister 엔진을 초기화
    std::uniform_real_distribution<double> dis(1.0, (-10)); // 10.0 ~ 0.001 사이의 균일 분포

    for (int i = 0; i < shape_size[0]; ++i)
    {
        for (int j = 0; j < shape_size[1]; ++j)
        {
            for (int k = 0; k < shape_size[2]; ++k)
            {
                for (int l = 0; l < shape_size[3]; ++l)
                {
                    arr[i][j][k][l] = dis(gen);
                    ///arr[i][j][k][l] = ;
                }
            }
        }
    }
}

void print_SHAPE_LO_RO_VL(double ****spatialDataArr, const vector<long> &shape_size, const FVector &playerLocation, const FRotation &playerRotation)
{
    
    cout << "----------------[array shape start]-----------------" << endl;
    cout << "[" << shape_size[0] << ", " << shape_size[1] << ", " << shape_size[2] << ", " << shape_size[3] << "]" << endl;
    cout << "----------------[array shape end]-------------------" << endl;
    cout << "----------------[PlayerLocation start]----------------" << endl;
    cout << "[" << playerLocation.X << ", " << playerLocation.Y << ", " << playerLocation.Z << "]" << endl;
    cout << "----------------[PlayerLocation end]------------------" << endl
         << endl;
    cout << "----------------[PlayerRotation start]----------------" << endl;
    cout << "[" << playerRotation.Pitch << ", " << playerRotation.Roll << ", " << playerRotation.Yaw << "]" << endl;
    cout << "----------------[PlayerRotation end]------------------" << endl
         << endl;
}