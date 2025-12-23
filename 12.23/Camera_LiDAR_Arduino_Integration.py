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

    # Camera 연결 초기화
    print("Camera 연결 시도...")
    cam = fl.libCAMERA()
    # capnum=2로 설정하여 두 개의 카메라 채널 초기화 (ch0: 내장/기본, ch1: 외부/USB)
    ch0, ch1 = cam.initial_setting(capnum=2)
    print("Camera 연결 성공")

    print("Camera, LiDAR 및 Arduino 통합 제어 시작...")
    print("종료하려면 'q'를 누르거나 Ctrl+C를 누르세요.")

    try:
        # LiDAR 스캔 시작 (이 루프는 LiDAR 데이터가 들어올 때마다 반복됨)
        # 카메라 프레임 속도는 LiDAR 스캔 속도(약 10Hz)에 맞춰짐
        for scan in lidar.scanning():
            # 1. Camera 처리
            # 프레임 읽기
            _, frame0, _, frame1 = cam.camera_read(ch0, ch1)
            
            # 신호등 인식 (frame1 사용)
            # object_detection은 'RED', 'GREEN', 'BLUE', 'YELLOW' 문자열 또는 None 반환
            traffic_color = cam.object_detection(frame1, sample=16, print_enable=True)
            
            # 화면 갱신 및 종료 키('q') 확인
            if cam.loop_break():
                break

            # 2. LiDAR 처리
            # 170도 ~ 190도 사이의 데이터만 추출
            valid_points = lidar.getAngleRange(scan, 170, 190)

            # 유효한 포인트가 없으면 기본적으로 먼 거리로 간주하거나, 이전 상태 유지
            # 여기서는 안전을 위해 0으로 처리하거나, min_dist를 큰 값으로 설정
            if len(valid_points) == 0:
                min_dist = 9999 # 장애물 없음
            else:
                # 추출된 포인트 중 거리값(인덱스 1)만 가져오기
                distances = valid_points[:, 1]
                min_dist = min(distances)

            # 3. 통합 제어 로직
            val = ''
            status_msg = ""

            # 우선순위:
            # 1. 빨간불이면 무조건 정지
            # 2. 초록불이면 주행 (단, LiDAR 장애물 감지 시 회피/정지)
            
            if traffic_color == "RED":
                val = '0' # 정지
                status_msg = f"신호등: RED -> 정지"
            else:
                # 신호등이 GREEN이거나 감지되지 않을 때 -> LiDAR 자율 주행 로직 따름
                # (Green일 때 무작정 전진하면 벽에 박을 수 있으므로 LiDAR 퓨전 유지)
                
                # 거리 판단 (mm 단위)
                if min_dist < 300: # 30cm 이내
                    val = '0'
                    status_msg = f"장애물 감지({min_dist:.0f}mm) -> 정지"
                elif 300 <= min_dist < 700: # 30cm ~ 70cm
                    val = '1'
                    status_msg = f"장애물 근접({min_dist:.0f}mm) -> 감속"
                else: # 70cm 이상
                    val = '2' # 고속 주행 (Speed 255)
                    status_msg = f"주행 가능({min_dist:.0f}mm) -> 전진"
                
                if traffic_color == "GREEN":
                    status_msg = "[Green] " + status_msg

            # Arduino로 데이터 전송 (개행 문자 포함)
            comm.write((val + '\n').encode())
            
            # 상태 출력
            print(f"[통합제어] {status_msg} | 전송값: {val}")

    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        lidar.stop()
    except Exception as e:
        print(f"\n에러 발생: {e}")
        lidar.stop()

if __name__ == '__main__':
    main()
