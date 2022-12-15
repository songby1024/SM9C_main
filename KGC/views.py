import logging
from django.shortcuts import render
from django.http import FileResponse, HttpResponse, JsonResponse
from .gmssl.optimized_curve import curve_order as co
from .gmssl.sm9 import setup,private_key_extract,kem_dem_dec,kem_dem_enc,public_key_extract, verify, sign
from .gmssl.optimized_field_elements import FQ2
import pickle
import time
from django.views.decorators.csrf import csrf_exempt
import os
import json
import numpy as np
import jsonpickle
import uuid
from index import models


# class FqEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o,FQ2):
#             return{
#                 "coeffs" : o.coeffs,
#                 "modulus_coeffs": o.modulus_coeffs,
#                 "mc_tuples": o.mc_tuples,
#                 "degree": o.degree, 
#             }
#         else:
#             return super().default(o)

def handleFQ2(t):
    return FQ2(t['coeffs'])

@csrf_exempt
def index(request):
    print(request.method)
    if request.method == "GET":
        masterKey, privateKey = setup('encrypt')
        pickle.dump(masterKey, open('KGC/keys/master_public', 'wb'))
        pickle.dump(privateKey, open('KGC/keys/master_secret', 'wb'))
        return render(request, 'KGC/index.html')
    if request.method == "POST":
        btn1 = request.POST.get("btn1")
        if btn1 == "":
            return
        if btn1 == "1":
            time_data = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            masterKey, privateKey = setup('encrypt')
            pickle.dump(masterKey, open('KGC/keys/master_public', 'wb'))
            pickle.dump(privateKey, open('KGC/keys/master_secret', 'wb'))
            data = {"getkeys": "请求已收到， 正在生成服务器主公钥以及主私钥...",
                    "master_public": "主公钥已生成！", 
                    "master_secret": "主私钥已生成！", 
                    "time_mod": time_data,
                    "Link": "#"}
            return JsonResponse(data)
            
def apiPubParameter(request):
    data = {"n": "[" + str(co) + "]"}
    data = json.dumps(data)
    return render(request, "KGC/publicparame.html", {"data": data})



def createPrivateKey(request):
    #生成kgc主公私钥对
    kgc_master_public, kgc_master_secret = setup ('encrypt')
    pickle.dump(kgc_master_public, open('KGC/keys/kgc_master_public', 'wb'))
    pickle.dump(kgc_master_secret, open('KGC/keys/kgc_master_secret', 'wb'))
    with open("KGC/keys/kgc_master_public", "rb") as f:
        kgc_master_public = pickle.load(f)
    with open("KGC/keys/kgc_master_secret", "rb") as f:
        kgc_master_secret = pickle.load(f)
    #生成RA私钥
    RaPrivatekey = private_key_extract("encrypt",kgc_master_public,kgc_master_secret,"RAID001")
    pickle.dump(RaPrivatekey, open('KGC/keys/kgc_ra_secret', 'wb'))
    #生成RA公钥
    RaPublicKey = public_key_extract("encrypt",kgc_master_public,"RAID001")
    pickle.dump(RaPublicKey, open('KGC/keys/kgc_ra_public', 'wb'))
    return HttpResponse(11)

def generateUid():
    uid = uuid.uuid1()
    sid = uuid.uuid1()
    models.Demo.objects.create(UID = uid,SID = sid)
    return HttpResponse('OK')


#加密函数
def encode(request):
    # message = ['ASD123871asdsDL','114514','1668306570','7549872']
    message = 'a123'
    #message = json.dumps(message)
    idA = "KGC001"
    with open("KGC/keys/kgc_master_public", "rb") as f:
        kgc_master_public = pickle.load((f))
    
    ct = kem_dem_enc(kgc_master_public, idA, message, 32)  # 密文
        # ct =  pickle.dumps(ct)
    pickle.dump(ct, open("KGC/keys/ct", "wb"))
    return HttpResponse(11)



#解密
def decode(request):
    with open("KGC/keys/kgc_master_public", "rb") as f:
        kgc_master_public = pickle.load(f)
    idA = "KGC001"
    with open("KGC/keys/kgc_master_secret", "rb") as f:
        kgc_master_secret = pickle.load((f))
    # with open("KGC/keys/ct", "rb") as f:
    #     message = pickle.loads((f.read()))  
    with open('KGC/keys/ct', 'rb') as f:
        message = pickle.load(f)
    Da = private_key_extract ('encrypt', kgc_master_public, kgc_master_secret, idA) # 私钥
    pt = kem_dem_dec (kgc_master_public, idA, Da, message, 32)
    print(pt)
    return HttpResponse(pt)


def PPS(request):
    RAID = "RAID001"
    with open("KGC/keys/master_public", "rb") as f:
        PKGPubKey = pickle.loads((f.read()))
    #生成RA公钥
    RAPubkey = public_key_extract("encrypt",PKGPubKey,RAID)
    data = [RAID,PKGPubKey,RAPubkey]
    datas =  pickle.dump(data, open('KGC/keys/PPS', 'wb'))
    response = FileResponse(open(r"KGC/keys/PPS", "rb"))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment;filename=pps.guet"  # 注意filename不支持中文
    return response
    

def sign_key(request):
    master_public, master_secret = setup ('sign')
    pickle.dump(master_public, open('KGC/keys/sign_master_public', 'wb'))
    pickle.dump(master_secret, open('KGC/keys/sign_master_secret', 'wb'))
    #K生成签名主公私钥
    with open('KGC/keys/sign_master_public', 'rb') as f:
        sign_master_public = pickle.load(f)
    with open('KGC/keys/sign_master_secret', 'rb') as f:
        sign_master_secret = pickle.load(f)
    idA = 'RAID001'
    #生成RA签名私钥
    ra_sign_key = private_key_extract ('sign',sign_master_public, sign_master_secret, idA)
    pickle.dump(ra_sign_key, open('KGC/keys/ra_sign_key', 'wb'))
    with open('KGC/keys/ct', 'rb') as f:
        message = pickle.load(f)
    message = str(message)
    signature = sign (sign_master_public, ra_sign_key, message)
    pickle.dump(signature, open('KGC/keys/sign_data', 'wb'))
    return HttpResponse(12)


def check_sign(request):
    with open('KGC/keys/sign_master_public', 'rb') as f:
        master_public = pickle.load(f)
    with open('KGC/keys/sign_data', 'rb') as f:
        signature = pickle.load(f)
    with open('KGC/keys/ct', 'rb') as f:
        message = pickle.load(f)
    message = str(message)
    idA = 'RAID001'
    if verify(master_public, idA, message, signature):
        return HttpResponse(200)
    else:
        return HttpResponse(403)


@csrf_exempt
def abc(request):
    data = request.FILES.get("data")
    with open('KGC/keys/sign_master_public', 'rb') as f:
        master_public = pickle.load(f)
    datas = pickle.load(data)
    signature = datas[2]
    with open('KGC/keys/ct', 'rb') as f:
        message = pickle.load(f)
    message = str(message)
    idA = 'RAID001'
    if verify(master_public, idA, message, signature):

        return HttpResponse(200)
    else:
        return HttpResponse(403)
    # return HttpResponse(200)