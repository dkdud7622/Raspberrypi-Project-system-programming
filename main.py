from CameraService import CameraService
from model import object_recognition, getDistanceByWidth
import time
import socket
from threading import Thread

cap = CameraService(0)
cap.start()


def getDistances():
    distances = []
    objects = object_recognition(cap.snapshot())
    for object in objects:
        score = object.image_object_detection.score
        vertices = object.image_object_detection.bounding_box.normalized_vertices
        width = vertices[1].x - vertices[0].x
        distances.append((score, getDistanceByWidth(width)))

    return distances

# distance에서 스코어를 가져옵니다


def get_score(distance):
    return distance[0]

# 쓰레드에서 실행되는 코드입니다.
# 접속한 클라이언트마다 새로운 쓰레드가 생성되어 통신을 하게 됩니다.


def task(client_socket, addr):
    # 클라이언트가 접속을 끊을 때 까지 반복합니다.
    try:
        while True:
            #거리 측정
            distances = getDistances()            
            
            if len(distances) == 0:
                #거리 측정 실패시 -1로 전송 문자열 설정
                payload = '-1\r\n'
            else:
                #거리 측정 성공시 스코어 순으로 오름차순 정렬
                distances.sort(key=get_score)
                #가장 높은 점수의 거리를 distance로 설정
                _, distance = distances[-1]
                # distance 전송 문자열 생성
                payload = f'{distance}\r\n'

            #전송 문자열을 바이트로 인코딩
            payload = payload.encode()
            #클라이언트에 전송
            client_socket.send(payload)
            print(f'send: {addr[0]}:{addr[1]}, {len(payload)}, {payload}')
            #0.1초 대기
            time.sleep(0.1)

    except ConnectionResetError:
        # 클라이언트에서 연결 종료
        pass
    except BrokenPipeError:
        # 클라이언트에서 연결 종료
        pass
    finally:
        # 클라이언트 통신 정리
        client_socket.close()
        print('Disconnected by ' + addr[0], ':', addr[1])


HOST = '127.0.0.1'
PORT = 7040

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print('Server start')

# 클라이언트가 접속하면 accept 함수에서 새로운 소켓을 리턴합니다.
# 새로운 쓰레드에서 해당 소켓을 사용하여 통신을 하게 됩니다.
while True:
    # 클라이언트 요청 대기
    client_socket, addr = server_socket.accept()
    print(f'Accept: ', addr)
    # 클라이언트 실행
    Thread(target=task, args=(client_socket, addr)).run()
