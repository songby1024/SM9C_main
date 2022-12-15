import sys

from PySide2 import QtCore, QtWebSockets, QtNetwork
from PySide2.QtCore import QUrl, QCoreApplication, QTimer
from PyQt5.QtWidgets import QApplication
import requests

class ClientWS:
    def __init__(self):
        super().__init__()

        self.client = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13,None)
        self.client.error.connect(self.error)

        self.client.open(QUrl("ws://202.193.56.108:8000/room/123"))
        self.client.pong.connect(self.onPong)

    def do_ping(self):
        print("client: do_ping")
        self.client.ping(b"foo")

    def request(self,str):
        print("do_request")

        print(req)
        # self.client.request()
        
    def send_message(self,message):
        print("client: send_message")
        self.client.sendTextMessage(message)

    def onPong(self, elapsedTime, payload):
        print("onPong - time: {} ; payload: {}".format(elapsedTime, payload))

    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.client.errorString())

    def close(self):
        self.client.close()

def quit_app():
    print("timer timeout - exiting")
    QCoreApplication.quit()

