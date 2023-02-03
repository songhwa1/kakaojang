# GUI 채팅 클라이언트
import time
from socket import *
from threading import *
import sys
import datetime
import pymysql
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets
form_class = uic.loadUiType('eh_chatting.ui')[0]

class ChatClient(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.overlap = 0

        # 페이지 이동
        self.main1_Button.clicked.connect(self.move_home)
        self.main2_Button.clicked.connect(self.move_home)
        self.enter_Button.clicked.connect(self.move_chatroom)
        self.mychat_tableWidget.cellClicked.connect(self.move_chatting)
        self.before_Button.clicked.connect(self.move_chatroom)

        self.initialize_socket(ip,port)
        self.listen_thread()
        self.push_Button.clicked.connect(self.send_chat)
        # self.pastmsg_Button.clicked.connect(self.past_contents)
        self.createChat_Button.clicked.connect(self.send_newroom)

        # tableWidget 열 넓이 조정
        self.mychat_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # ---실험중---
        self.stackedWidget.setCurrentIndex(0)
        self.show_room()


    def move_home(self):
        self.stackedWidget.setCurrentIndex(0)
    def move_chatroom(self):
        self.msg_listWidget.clear()
        self.show_room()
        self.msg_listWidget_2.clear()
        self.stackedWidget.setCurrentIndex(1)
    def move_chatting(self):
        self.selectRoom = (self.mychat_tableWidget.currentItem().text())
        self.senders_name = self.name_lineEdit.text().strip()
        self.send_room()    # 채팅방 이름 서버로 보내기
        self.save_people()  # 채팅방 입장한 인원 db에 저장
        print('현재입장한방', self.selectRoom)
        self.roomname_label.setText(self.selectRoom)
        self.stackedWidget.setCurrentIndex(2)

    def initialize_socket(self,ip,port):
        '''
        TCP socket을 생성하고 server와 연결
        '''
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.remote_ip = ip
        self.remote_port = port
        self.client_socket.connect((self.remote_ip, self.remote_port))

    def send_chat(self):
        '''
        message를 전송하는 버튼 콜백 함수
        '''
        self.msg_data = self.send_lineEdit.toPlainText().strip()
        self.msg_listWidget.scrollToBottom()
        self.msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.send_info()
        print(self.msg_time)
        self.send_lineEdit.clear()
        return 'break'

    def send_room(self):
        rname = ['###', self.selectRoom]
        roomname = str(rname).encode()
        self.client_socket.send(roomname)

    def send_info(self):
        info = ['@@@',self.remote_ip, self.senders_name, self.selectRoom, self.senders_name, self.msg_time, self.msg_data]
        total_info = str(info).encode()
        self.client_socket.send(total_info)

    def send_newroom(self):
        self.senders_name = self.name_lineEdit.text().strip()
        new_room = self.createChat_lineEdit.text()
        nroom_list = ['+++', new_room, self.senders_name]
        nroom = str(nroom_list).encode()
        self.client_socket.send(nroom)
        time.sleep(0.1)
        if self.overlap == 1:
            QMessageBox.information(self, '알림', '이미 있는 채팅방입니다')
            self.overlap = 0
        else:
            print(self.overlap)
            time.sleep(0.7)
            self.show_room()

    def listen_thread(self):
        '''
        데이터 수신 Tread를 생성하고 시작한다
        '''
        t = Thread(target=self.receive_message, args=(self.client_socket,))
        t.start()

    def show_room(self):
        self.mychat_tableWidget.clear()
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        a = conn.cursor()
        # 채팅방이름 불러오기
        sql = f"SELECT distinct ROOM FROM chatting"
        a.execute(sql)
        room_info = a.fetchall()    # 이중 튜플((채팅방이름),)
        print(room_info)
        row = 0
        self.mychat_tableWidget.setRowCount(len(room_info))
        for i in room_info:
            self.mychat_tableWidget.setItem(row, 0, QTableWidgetItem(str(i[0])))
            row += 1
        conn.close()

    def receive_message(self, so):
        while True:
            buf = so.recv(10000)
            if not buf: # 연결이 종료됨
                break
            buf_data = buf.decode()
            print('중복: ', buf_data)
            # 지난 내용 불러오기
            if buf_data[2:5] == '%%%':  # 지난 내용 식별자
                recv_data = eval(buf.decode())
                print(1,recv_data)
                past_msg = recv_data[1:]    # 식별자 제외한 진짜 정보
                print(2,past_msg)
                for i in past_msg:
                    self.msg_listWidget.addItem(f'{i[0]}:{i[1]}')
                    self.msg_listWidget.scrollToBottom()

            # 참여 인원 불러오기
            elif buf_data[2:5] == '&&&':    # 참여 인원 식별자
                recv_data1 = eval(buf.decode())
                enter_people = recv_data1[1:]
                print('참여인원',enter_people)
                for i in enter_people:
                    self.msg_listWidget_2.addItem(i)
                    self.msg_listWidget.scrollToBottom()

            # 채팅방 이름 중복
            elif buf_data[0:4] == '중복됨':
                print(3)
                self.overlap = 1
                print(4)
            # 실시간 채팅 추가
            else:
                self.msg_listWidget.addItem(buf_data)
                self.msg_listWidget.scrollToBottom()
        so.close()

    # def past_contents(self):
    #     # MySQL에서 import 해오기
    #     conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
    #                            db='kakaojang')
    #     a = conn.cursor()
    #     # 채팅방 지난 내용 불러오기
    #     sql = f"SELECT NAME, LETTER FROM data where ROOM = '{self.selectRoom}'"
    #     a.execute(sql)
    #     letter_info = a.fetchall()  # 이중 튜플((이름, 메시지,),(이름, 메세지,))
    #     print(letter_info)
    #     for i in letter_info:
    #         self.msg_listWidget.addItem(f'{i[0]}:{i[1]}')

    def save_people(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        a = conn.cursor()
        sql = f"insert into chatting(ROOM, NAME) values('{self.selectRoom}', '{self.senders_name}')"
        a.execute(sql)
        conn.commit()
        conn.close()



if __name__ == '__main__':
    ip = '10.10.21.123'
    port = 5010

    app = QApplication(sys.argv)

    widget = QtWidgets.QMainWindow

    mainWindow = ChatClient()

    mainWindow.show()
    app.exec_()
