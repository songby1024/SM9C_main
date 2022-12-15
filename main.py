import os
import pickle
import random
import time
import wget
from PySide2.QtUiTools import QUiLoader
from ClientWS import *
from KGC.gmssl.main import encode_demo
from KGC.gmssl.sm4 import CryptSM4, SM4_DECRYPT


class LoginUI:

    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("UI/login.ui")
        self.ui.signin.clicked.connect(self.signin)

    # 登录响应
    def signin(self):
        # 先删除已存在的文件
        if os.path.isfile('pps.guet'):
            os.remove("pps.guet")
        url = "http://202.193.56.108:8000/kgc/api/PPS"
        path = "pps.guet"
        # 从pps下载参数文件（公钥）
        wget.download(url, path)

        with open('pps.guet', 'rb') as f:
            data = pickle.load(f)
            # print(data[0])  # RAID
            # print(data[1])  # PKG-PK(RA-PK)

        # 生成随机数和时间戳
        random_1 = random.randint(0000000000000000, 9999999999999999)  # 随机数
        t = int(round(time.time() * 1000))  # 时间戳
        # id = self.ui.loginid.text()  # 用户ID
        # password = self.ui.loginpassword.text()  # 用户密码
        # payload = {'username': id, 'password': password}  # 用户信息序列
        # fileName = 'note.txt'
        # with open(fileName, 'w', encoding='utf-8') as file:
        #     file.write("id:" + id + "%n" + password + "\n")
        #     file.write("随机数:" + hash.__str__() + "\n" + "时间戳:" + t.__str__())
        # file.close()

        # （UID||RAID||T1||R1）写入文件
        pickle.dump(["UID001", data[0], str(t), random_1], open('note.txt', 'wb'))
        # 再从里面读取数据
        with open('note.txt', 'rb') as file:
            val = pickle.load(file)

        # 用PKG-PK加密SID
        SID = encode_demo("KGC001", "SID001", data[1])
        # 用RA-PK加密UID||RAID||T1||R1
        UID = encode_demo(data[0], str(val), data[2])
        with open('test1', 'wb') as f:
            f.write(SID)
        with open('test2', 'wb') as f:
            f.write(UID)

        # 向RA发送数据
        url = 'http://202.193.56.108:8080/api/ma'
        files = {'SID': SID, "UID": UID}
        r = requests.post(url, files=files)
        mes1 = r.content

        # 解密返回的r.text
        crypt_sm4 = CryptSM4()
        key = random_1.to_bytes(16, 'big')
        crypt_sm4.set_key(key, SM4_DECRYPT)
        decrypt_value = pickle.loads(crypt_sm4.crypt_ecb(mes1))
        print(decrypt_value)

        # 获得de_UID,TOKEN,random_2,做判断
        de_UID = decrypt_value[0][2:8]
        TOKEN = decrypt_value[0][12:59]
        random_2 = decrypt_value[2]
        print("de_UID")
        print(de_UID)
        print("TOKEN")
        print(TOKEN)
        print("random_2")
        print(random_2)
        if de_UID != "UID001":
            return

        # KDF生成CK和IK

        # 生成时间戳T2
        t2 = int(round(time.time() * 1000))  # 时间戳


        global mainui
        mainui = MainUI()
        mainui.ui.show()
        self.ui.close()

    # 注册响应
    # def signup(self):
    #     ws.send_message()


class MainUI:

    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("UI/main.ui")
        self.ui.get_privatekey.clicked.connect(self.get_privatekey)

    def get_privatekey(self):
        hash = random.getrandbits(128)
        t = time.time()
        print(id)


if __name__ == '__main__':
    global login
    global ws

    app = QApplication(sys.argv)

    login = LoginUI()
    login.ui.show()
    # ws = ClientWS()
    # ws.send_message()

    sys.exit(app.exec_())
