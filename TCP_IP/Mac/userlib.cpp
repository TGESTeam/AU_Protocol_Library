#include "library.hpp"


int main(){
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