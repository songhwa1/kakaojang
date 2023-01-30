# GUI 채팅 클라이언트
from socket import *
from threading import *
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets
form_class = uic.loadUiType('eh_chatting.ui')[0]

class ChatClient(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.initialize_socket(ip,port)
        self.listen_thread()
        self.pushButton.clicked.connect(self.send_chat)

    def initialize_socket(self,ip,port):
        '''
        TCP socket을 생성하고 server와 연결
        '''

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip, remote_port))

    def send_chat(self):
        '''
        message를 전송하는 버튼 콜백 함수
        '''
        senders_name = self.name_lineEdit.text().strip()+":"
        data = self.send_lineEdit.text().strip()
        message = (senders_name + data).encode('utf-8')
        self.listWidget.addItem(message.decode('utf-8'))
        self.listWidget.scrollToBottom()
        self.client_socket.send(message)
        self.send_lineEdit.clear()
        return 'break'


    def listen_thread(self):
        '''
        데이터 수신 Tread를 생성하고 시작한다
        '''

        t = Thread(target=self.receive_message, args=(self.client_socket,))
        t.start()

    def receive_message(self, so):
        while True:
            buf = so.recv(256)
            if not buf: # 연결이 종료됨
                break
            self.listWidget.addItem(buf.decode('utf-8'))
            self.listWidget.scrollToBottom()
        so.close()

if __name__ == '__main__':
    ip = '10.10.21.123'
    port = 5010

    app = QApplication(sys.argv)

    widget = QtWidgets.QMainWindow

    mainWindow = ChatClient()

    # widget.addWidget(mainWindow)

    # widget.setFixedWidth(569)
    # widget.setFixedHeight(582)

    mainWindow.show()
    app.exec_()
