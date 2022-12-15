from PyQt5 import QtWidgets
# from PyQt5 import uic

class Signup:

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("UI/signup.ui")

        self.ui.clear.clicked.connect(self.clear)
        self.ui.signup.clicked.connect(self.signup)

    # 登录响应
    def clear(self):
        # global main_win
        # main_win = None
        self.ui.close()

    # 注册响应
    def signup(self):
        self.ui.close()
        # global main_win
        # # 实例化另外一个窗口
        # main_win = signup()
        # # 显示新窗口
        # main_win.ui.show()
        # self.ui.close()