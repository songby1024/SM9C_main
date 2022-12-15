import hmac
import os
from PySide2.QtUiTools import QUiLoader
import random
from ClientWS import *
import time
import wget
import pickle
from KGC.gmssl.main import encode_demo
from KGC.gmssl.sm4 import CryptSM4, SM4_DECRYPT, SM4_ENCRYPT
from SM9C.KGC.gmssl.sm3 import sm3_kdf

encrypt_value = ''
HmacUserIK = ''


class demoUi:

    def __init__(self):

        super().__init__()
        self.ui = QUiLoader().load("UI/demo.ui")
        self.ui.identification.clicked.connect(self.identification)
        self.ui.signIn.clicked.connect(self.signIn)

    def identification(self):
        # 先删除文本框里面的文字
        self.ui.textBrowser.clear()
        # 先删除已存在的文件
        if os.path.isfile('pps.guet'):
            os.remove("pps.guet")
        url = "http://202.193.56.108:8000/kgc/api/PPS"
        path = "pps.guet"
        # 从pps下载参数文件（公钥）
        wget.download(url, path)
        self.ui.textBrowser.append("从PPS下载参数文件\n")
        with open('pps.guet', 'rb') as f:
            data = pickle.load(f)
        self.ui.textBrowser.append("\n获取RAID:\n" + data[0])
        self.ui.textBrowser.append("\n获取PGKPK:\n" + str(data[1]))

        random_1 = random.randint(1000000000000000, 9999999999999999)  # 随机数
        print("random_1")
        print(random_1)
        self.ui.textBrowser.append("\n生成随机数:\n" + str(random_1))
        t = int(round(time.time() * 1000))  # 时间戳
        self.ui.textBrowser.append("\n生成时间戳:\n" + str(t))

        # UID | | RAID | | T1 | | R1）写入文件
        pickle.dump(["<UID001>", data[0], str(t), '<' + str(random_1) + '>'], open('note.txt', 'wb'))
        # 再从里面读取数据
        with open('note.txt', 'rb') as file:
            val = pickle.load(file)

        # 用PKG-PK加密SID
        SID = encode_demo("KGC001", "SID001", data[1])
        self.ui.textBrowser.append("\n用PKG-PK加密SID:\n" + str(SID))
        # 用RA-PK加密UID||RAID||T1||R1
        UID = encode_demo(data[0], str(val), data[2])
        self.ui.textBrowser.append("\n用RA-PK加密UID||RAID||T1||R1:\n" + str(UID))
        with open('test1', 'wb') as f:
            f.write(SID)
        with open('test2', 'wb') as f:
            f.write(UID)

        # 向RA发送数据
        url = 'http://202.193.56.108:8080/api/ma'
        files = {'SID': SID, "UID": UID}
        r = requests.post(url, files=files)
        self.ui.textBrowser.append("\n向RA发送密文\n")
        mes1 = r.content
        self.ui.textBrowser.append("\n得到传回的内容\n" + str(mes1))

        # 解密返回的r.text
        crypt_sm4 = CryptSM4()
        key = random_1.to_bytes(16, 'big')
        crypt_sm4.set_key(key, SM4_DECRYPT)
        decrypt_value = pickle.loads(crypt_sm4.crypt_ecb(mes1))
        self.ui.textBrowser.append("\n解密内容\n" + str(decrypt_value))
        print(decrypt_value)

        # 获得de_UID,TOKEN,random_2,做判断
        de_UID = decrypt_value[0][8:14]
        TOKEN = decrypt_value[0][24:71]
        random_2 = decrypt_value[2]
        print("de_UID")
        print(de_UID)
        self.ui.textBrowser.append("\n解析回传UID:\n" + str(de_UID))
        print("TOKEN")
        print(TOKEN)
        self.ui.textBrowser.append("\n解析回传TOKEN\n" + str(TOKEN))
        print("random_2")
        print(random_2)
        self.ui.textBrowser.append("\n解析回传随机数\n" + str(random_2))

        # 对比UID与de_UID的一致性
        if de_UID != "UID001":
            return

        # KDF生成CK和IK
        # temp = sm3_kdf(str(random_1 ^ random_2).encode(), 16)
        ran1_xor_ran2 = str(random_1 ^ random_2)
        while len(ran1_xor_ran2) < 16:
            ran1_xor_ran2 += '0'
        while len(ran1_xor_ran2) > 16:
            ran1_xor_ran2 = ran1_xor_ran2[:-1]
        temp = sm3_kdf(bytes(ran1_xor_ran2, 'utf-8'), 16)

        CK = temp[:16]
        IK = temp[16:]
        self.ui.textBrowser.append("\n通过KDF生成的CK为：\n" + CK)
        self.ui.textBrowser.append("\n通过KDF生成的IK为：\n" + IK)

        # 生成时间戳T2
        t2 = int(round(time.time() * 1000))  # 时间戳

        # 用ck加密：UID||T2||用户资料
        mes2 = str(("UID001" + ',' + str(t2) + ',' + "this is a message"))
        key = bytes(CK, encoding="utf-8")
        crypt_sm4.set_key(key, SM4_ENCRYPT)
        global encrypt_value
        encrypt_value = (crypt_sm4.crypt_ecb(bytes(mes2, encoding="utf-8")))
        self.ui.textBrowser.append("\n(UID||T2||用户资料)以CK为密钥经SM4加密后的密文：\n" + str(encrypt_value))
        print(encrypt_value)

        # 将加密的encrypt_value进行哈希用IK
        global HmacUserIK
        HmacUserIK = hmac.new(bytes(IK, encoding="utf-8"), encrypt_value)
        self.ui.textBrowser.append("\n将加密的密文进行哈希处理：\n" + str(HmacUserIK.digest()))
        print("HmacUserIK")
        print(HmacUserIK.digest())

        self.ui.textBrowser.append("\n现在可以点击注册按钮进行注册了\n")

    def signIn(self):
        self.ui.textBrowser_2.append("\n正在申请注册中………………\n\n")
        # 发送注册请求
        # UID||ECK||HIK
        pickle.dump({'uid': "UID001", 'res1': encrypt_value, 'res2': HmacUserIK.digest()},
                    open("dump1.text", "wb"))
        files = {'file': open('dump1.text', 'rb')}
        res = requests.post("http://202.193.56.108:8080/api/register", files=files)
        print(res.content)
        if res.content.decode() == '200':
            msg = '恭喜你，注册成功'
        else:
            msg = '注册失败'
        self.ui.textBrowser_2.append("响应结果：\n" + msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = demoUi()
    demo.ui.show()

    sys.exit(app.exec_())
