# _*_ coding: utf-8 _*_
# @File : fuckenglish.py
# @Date : 2022-10-23-20:58
# @Software : PyCharm
import requests
import time
url = 'https://zhihui.guet.edu.cn/stu/webuc/lookjx.aspx?jxid=667&u=90432&tcid=328&name=727729285&ram=0.2830870240734229&zjs=70'
headers = {
    'authority': 'zhihui.guet.edu.cn',
    'method': 'GET',
    'path': '/stu/webuc/lookjx.aspx?jxid=667&u=90432&tcid=328&name=727729285&ram=0.5869356918249427&zjs=5',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'ASP.NET_SessionId=tykga145lei3pteddnbrtvyd; T_Stu=userid=90432; cstime992=timging=2022/10/31 9:56:13',
    'referer': 'https://zhihui.guet.edu.cn/stu/Shownews.aspx?id=667',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}
while True:
    req = requests.get(url=url, headers=headers)
    print(req.text)
    time.sleep(0.4)
