# GUI 채팅 클라이언트
from socket import *
from threading import *
import sys

import pymysql
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets
form_class = uic.loadUiType('eh_chatting.ui')[0]

class ChatClient(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 페이지 이동
        self.main1_Button.clicked.connect(self.move_home)
        self.main2_Button.clicked.connect(self.move_home)
        self.enter_Button.clicked.connect(self.move_chatroom)
        self.mychat_tableWidget.cellClicked.connect(self.move_chatting)


        self.initialize_socket(ip,port)
        self.listen_thread()
        self.push_Button.clicked.connect(self.send_chat)

        # tableWidget 열 넓이 조정
        self.mychat_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # ---실험중---
        self.stackedWidget.setCurrentIndex(0)
        self.show_room()


    def move_home(self): #메인화면
        self.stackedWidget.setCurrentIndex(0)
    def move_chatroom(self): #나의채팅방목록보여주기
        self.stackedWidget.setCurrentIndex(1)
    def move_chatting(self): #채팅방
        self.selectRoom = (self.mychat_tableWidget.currentItem().text())
        print('현재입장한방',self.selectRoom)
        self.roomname_label.setText(self.selectRoom)
        self.stackedWidget.setCurrentIndex(2)
        # self.past_contents()  #이전 컨텐츠 불러오기

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
        self.senders_name = self.name_lineEdit.text().strip()
        self.msg_data = self.send_lineEdit.toPlainText().strip()
        message = (self.senders_name + ":" + self.msg_data).encode('utf-8')
        self.msg_listWidget.addItem(message.decode('utf-8'))
        self.msg_listWidget.scrollToBottom()
        self.client_socket.send(message)
        self.save_message()  # 메세지 DB에 저장하는 함수 불러움
        self.send_lineEdit.clear()
        return 'break'

    def listen_thread(self):
        '''
        데이터 수신 Tread를 생성하고 시작한다
        '''
        t = Thread(target=self.receive_message, args=(self.client_socket,))
        t.start()

    def show_room(self): #mychat_tableWidget 에 kakaojang.chatting ROOM 목록 넣기
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        a = conn.cursor()
        # 채팅방이름 불러오기
        sql = f"SELECT * FROM chatting"
        a.execute(sql)
        room_info = a.fetchall()    # 이중 튜플((채팅방이름, 보낸사람),)
        print('dbRoom,Name',room_info)
        row = 0
        self.mychat_tableWidget.setRowCount(len(room_info))
        for i in room_info:
            self.mychat_tableWidget.setItem(row, 0, QTableWidgetItem(str(i[0])))
            row += 1
        conn.close()
        self.roomname_label.setText(room_info[0][0])    # 채팅방 이름 보여주기

    def receive_message(self, so):
        while True:
            buf = so.recv(256)
            if not buf: # 연결이 종료됨
                break
            self.msg_listWidget.addItem(buf.decode('utf-8'))
            self.msg_listWidget.scrollToBottom()
        so.close()

    def save_message(self):
        self.room_name = self.roomname_label.text()
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        a = conn.cursor()
        # 채팅방이름 불러오기
        sql = f"insert into data(IP, NAME, ROOM, SENDER, DATETIME, LETTER) values ('{self.remote_ip}', '{self.senders_name}', '{self.selectRoom}', '{self.senders_name}', {'now()'}, '{self.msg_data}')"
        a.execute(sql)
        conn.commit()
        conn.close()

    def past_contents(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.123', port=3306, user='eh', password='0000',
                               db='kakaojang')
        a = conn.cursor()
        # 채팅방 지난 내용 불러오기
        sql = f"SELECT LETTER FROM data where ROOM = '{self.room_name}'"
        a.execute(sql)
        letter_info = a.fetchall()  # 이중 튜플((메시지),)
        print(letter_info)
        #for i in letter_info:
            #self.msg_listWidget.addItem()



if __name__ == '__main__':
    ip = '10.10.21.115'
    port = 5010

    app = QApplication(sys.argv)

    widget = QtWidgets.QMainWindow

    mainWindow = ChatClient()

    # widget.addWidget(mainWindow)

    # widget.setFixedWidth(569)
    # widget.setFixedHeight(582)

    mainWindow.show()
    app.exec_()
