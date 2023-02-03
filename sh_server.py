#threading 모듈을 이용한 TCP 멀티 채팅 GUI 프로그램
from socket import *
from threading import *

import pymysql


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
                incoming_info = c_socket.recv(256)
                if not incoming_info:    # 연결이 종료됨
                    break
            except:
                continue
            else:
                self.final_received_info = eval(incoming_info.decode())
                if self.final_received_info[0] == '@@@':    # db에 저장할 데이터들
                    print(self.final_received_info)
                    self.send_all_clents(c_socket)
                    self.save_message() # DB에 저장

                elif self.final_received_info[0] == '###':  # 채팅방 이름
                    print(self.final_received_info)
                    self.past_contents()    # 지난 내용 불러오는 메서드
                    self.send_pastmsg(c_socket)
                    self.entered_people()   # 참여인원 메서드
                    self.send_people(c_socket)

                elif self.final_received_info[0] == '+++':  # 새로 만든 채팅방 데이터
                    print(self.final_received_info)
                    self.save_newroom(c_socket)
        c_socket.close()

    def save_message(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        a = conn.cursor()
        sql = f"insert into data(IP, NAME, ROOM, SENDER, DATETIME, LETTER) values ('{self.final_received_info[1]}', '{self.final_received_info[2]}', '{self.final_received_info[3]}', '{self.final_received_info[4]}', '{self.final_received_info[5]}', '{self.final_received_info[6]}')"
        a.execute(sql)
        conn.commit()
        conn.close()

    def save_newroom(self, senders_socket):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        a = conn.cursor()
        sql2 = f"SELECT distinct ROOM FROM chatting"
        a.execute(sql2)
        room_info = a.fetchall()
        print(room_info)
        for i in range(len(room_info)):
            print(self.final_received_info[1] in room_info[i][0])
            if self.final_received_info[1] in room_info[i][0]:
                for client in self.clients:
                    socket, (ip, port) = client
                    text = '중복됨'
                    senders_socket.sendall(text.encode())
                return
        sql = f"insert into chatting(ROOM, NAME) values('{self.final_received_info[1]}', '{self.final_received_info[2]}')"
        a.execute(sql)
        conn.commit()
        conn.close()

    def past_contents(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        a = conn.cursor()
        # 채팅방 지난 내용 불러오기
        sql = f"SELECT NAME, LETTER FROM data where ROOM = '{self.final_received_info[1]}'"
        a.execute(sql)
        letter_info = a.fetchall()  # 튜플(%%%, ((이름, 메시지,),(이름, 메세지,)))
        self.msg_list = ['%%%']
        for i in letter_info:
            self.msg_list.append(list(i))
        print('채팅내용',self.msg_list)

    def entered_people(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        with conn:
            with conn.cursor() as a:
                sql2 = f"SELECT distinct NAME FROM chatting where ROOM = '{self.final_received_info[1]}'"
                a.execute(sql2)
                people_info = a.fetchall()  # 튜플((이름,), (이름,))
                print(people_info)
                self.people_list =['&&&']
                for j in people_info:
                    self.people_list.append(j[0])
        print('참여인원', self.people_list)


    def send_all_clents(self, senders_socket):
        # 발신자를 제외한 모든 연결 소켓으로 메세지 전송
        for client in self.clients: # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            print(client)
            # if socket is not senders_socket:    # 송신 클라이언트는 제외
            try:
                toclient_msg = self.final_received_info[2]+' : '+self.final_received_info[6]
                socket.sendall(toclient_msg.encode())
            except: # 연결 종료
                self.clients.remove(client) # 소켓 제거
                print(f'{ip}, {port} 연결이 종료되었습니다')
    def send_pastmsg(self, senders_socket):
        # self.past_contents()
        # 발신자를 제외한 모든 연결 소켓으로 메세지 전송
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(str(self.msg_list).encode())

    def send_people(self, senders_socket):
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(str(self.people_list).encode())



if __name__ == '__main__':
    MultiChatServer()

