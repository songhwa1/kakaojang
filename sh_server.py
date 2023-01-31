#threading 모듈을 이용한 TCP 멀티 채팅 GUI 프로그램
from socket import *
from threading import *


class MultiChatServer:
    def __init__(self):
        # 소켓 생성
        # 연결 대기
        # accept_client()를 호출하여 클라이언트와 연결
        self.clients = []
        self.final_received_message = ''    # 최종 수신 메세지
        self.s_sock = socket(AF_INET, SOCK_STREAM)
        self.ip = ''
        self.port = 5010
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_sock.bind((self.ip, self.port))
        print('클라이언트 대기중')
        self.s_sock.listen(100)
        self.accept_client()

    def accept_client(self):
        # 연결 수락
        # 연결 소켓 추가
        # 메시지 수신 스레드 생성/실행 (receive_message 함수)
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)     # 접속된 소켓을 목록에 추가
            print(ip, ':', str(port), '가 연결되었습니다')
            cth = Thread(target=self.receive_message, args=(c_socket,)) # 수신 스레드
            cth.start() # 스레드 시작


    def receive_message(self,c_socket):
        # 메세지 수신
        # send_all_clents() 호출(모든 클라이언트에게 전송)
        while True:
            try:
                incoming_message = c_socket.recv(256)
                if not incoming_message:    # 연결이 종료됨
                    break
            except:
                continue
            else:
                self.final_received_message = incoming_message.decode('utf-8')
                print(self.final_received_message)
                self.send_all_clents(c_socket)
        c_socket.close()

    def send_all_clents(self, senders_socket):
        # 발신자를 제외한 모든 연결 소켓으로 메세지 전송
        for client in self.clients: # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket:    # 송신 클라이언트는 제외
                try:
                    socket.sendall (self.final_received_message.encode())
                except: # 연결 종료
                    self.clients.remove(client) # 소켓 제거
                    print(f'{ip}, {port} 연결이 종료되었습니다')




if __name__ == '__main__':
    MultiChatServer()

