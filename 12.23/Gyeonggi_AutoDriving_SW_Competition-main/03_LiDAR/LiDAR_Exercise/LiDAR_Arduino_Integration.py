# Function_Library 라이브러리 불러오기
import Function_Library as fl

def main():
    # Arduino 포트 설정 (사용자 환경에 맞게 수정 필요)
    arduino_port = 'COM4'
    # LiDAR 포트 설정 (사용자 환경에 맞게 수정 필요)
    lidar_port = 'COM3'

    # 아두이노 연결 초기화
    print(f"아두이노 연결 시도: {arduino_port}")
    arduino = fl.libARDUINO()
    # 주의: Arduino_control.ino 코드가 9600 보드레이트를 사용하는지 확인 필요
    comm = arduino.init(arduino_port, 9600)
    print("아두이노 연결 성공")

    # LiDAR 연결 초기화
    print(f"LiDAR 연결 시도: {lidar_port}")
    lidar = fl.libLIDAR(lidar_port)
    lidar.init()
    print("LiDAR 연결 성공")

    print("LiDAR 및 Arduino 통합 제어 시작...")
    print("종료하려면 Ctrl+C를 누르세요.")

    try:
        # LiDAR 스캔 시작
        for scan in lidar.scanning():
            # 170도 ~ 190도 사이의 데이터만 추출
            # getAngleRange 함수는 (scan 데이터를, 최소각도, 최대각도)로 필터링하여 반환
            valid_points = lidar.getAngleRange(scan, 170, 190)

            # 유효한 포인트가 없으면 통과
            if len(valid_points) == 0:
                continue

            # 추출된 포인트 중 거리값(인덱스 1)만 가져오기
            distances = valid_points[:, 1]
            
            # 해당 범위 내에서 가장 가까운 거리를 기준으로 판단
            min_dist = min(distances)

            # Arduino로 보낼 값 결정
            # 거리 단위: mm (RPLidar 기본 단위)
            # 30cm = 300mm, 70cm = 700mm
            val = ''
            
            if min_dist < 300: # 30cm 이내
                val = '0'
            elif 300 <= min_dist < 700: # 30cm ~ 70cm
                val = '1'
            else: # 70cm 이상 (min_dist >= 700)
                val = '2'

            # Arduino로 데이터 전송
            # parseInt()가 구분을 할 수 있도록 개행 문자 추가
            comm.write((val + '\n').encode())
            
            # 디버깅을 위한 출력 (한글)
            # 현재 감지된 최소 거리와 전송한 값을 출력
            print(f"[상태] 각도: 170-190도, 최소거리: {min_dist:.2f}mm, 전송값: {val}")

    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        lidar.stop()

if __name__ == '__main__':
    main()
