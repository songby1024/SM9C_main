from KGC.gmssl import sm9, optimized_field_elements
import argparse
import hashlib
import base64
# from SM9C.KGC.gmssl import
# import optimized_field_elements
import pickle

# 盐 1
salt = "^&TG!@YBN34CASJ52IOCU&A*(SYs6DUH!@I)_@!$*!*^&)_AI"
aesKey = "*(AYSHUDNJASC*&!@)#OPINHASVDAS)"


def encode_demo(idA, message, master_public):
    # 加密
    # , master_secret = sm9.setup ('encrypt')
    ct = sm9.kem_dem_enc(master_public, idA, message, 32)  # 密文
    master_public = pickle.dumps(master_public)
    # master_secret = pickle.dumps(master_secret)
    cipherText = pickle.dumps(ct)
    # with open(str(idA) + "@master_public", "wb") as f:
    #     f.write(master_public)
    # print("[+] 加密主公钥已生成 --> " + str(idA) + "@master_public")
    # with open(str(idA) + "@master_secret", "wb") as f:
    #     f.write(master_secret)
    # print("[+] 加密主私钥已生成 --> " + str(idA) + "@master_secret")
    # with open(str(idA) + "@cipherText", "wb") as f:
    #     f.write(cipherText)
    print("[+] 密  文  已生成 --> " + str(idA) + " thank for you")
    return cipherText


def sign(message, idA):
    # 生成签名 主公钥     主私钥
    master_public, master_secret = sm9.setup('sign')
    Da = sm9.private_key_extract('sign', master_public, master_secret, idA)  # 签名私钥 不用分发
    # 这里设置成明文消息的加盐hash值 跟随消息发送过去
    md5Msg = message + salt
    msg = hashlib.md5()
    msg.update(md5Msg.encode())
    message = msg.hexdigest()
    signature = sm9.sign(master_public, Da, message)
    signPub = pickle.dumps(master_public)
    sign = pickle.dumps(signature)
    with open(str(idA) + "@sign", "wb") as f:
        f.write(sign)
    print("[+] 签  名  已生成 --> " + str(idA) + "@sign")
    with open(str(idA) + "@signPub", "wb") as f:
        f.write(signPub)
    print("[+] 签名公钥已生成 --> " + str(idA) + "@signPub")


def decode(idA):
    with open(str(idA) + "@master_public", "rb") as f:
        PubKey = pickle.loads((f.read()))
    with open(str(idA) + "@master_secret", "rb") as f:
        master_secret = pickle.loads(f.read())
    with open(str(idA) + "@cipherText", "rb") as f:
        message = pickle.loads(f.read())
    Da = sm9.private_key_extract('encrypt', PubKey, master_secret, idA)  # 私钥
    pt = sm9.kem_dem_dec(PubKey, idA, Da, message, 32)
    print("[+]密文: " + pt)


def check_sign(message, idA):
    with open(idA + "@signPub", "rb") as f:
        master_public = pickle.loads(f.read())
    with open(idA + "@sign", "rb") as f:
        signature = pickle.loads(f.read())
    md5Msg = message + salt
    msg = hashlib.md5()
    msg.update(md5Msg.encode())
    message = msg.hexdigest()
    if (sm9.verify(master_public, idA, message, signature)):
        print("[+] 签名验证通过")
    else:
        print("[-] 签名验证未通过")


if __name__ == "__main__":
    print("""
                                       
                                   
 .M\"\"\"bgd `7MMM.     ,MMF'         
,MI    \"Y   MMMb    dPMM           
`MMb.       M YM   ,M MM  .d*\"*bg. 
  `YMMNq.   M  Mb  M' MM 6MP    Mb 
.     `MM   M  YM.P'  MM YMb    MM 
Mb     dM   M  `YM'   MM  `MbmmdM9 
P\"Ybmmd\"  .JML. `'  .JMML.     .M' 
                             .d9   
                           m\"'          Designed By: Gu3t_S3c_T34m

    """)
    parser = argparse.ArgumentParser(description="input -h get help :)")
    parser.add_argument("-t", "--type", choices=["encode", "decode", "checkSign", "sign"], help="choose work mode")
    parser.add_argument("-i", "--id", help="input your id")
    parser.add_argument("-m", "--message", help="input your cipherText/plainText here")

    args = parser.parse_args()
    if args.type == "encode":
        assert (args.id != None), "please input your ID"
        encode_demo(args.id, args.message)
    if args.type == "decode":
        try:
            decode(args.id)
        except:
            print("[-] 解密失败")
    if args.type == "checkSign":
        check_sign(args.message, args.id)
    if args.type == "sign":
        sign(args.message, args.id)
