import requests
import csv
import hashlib
import time
from urllib.parse import quote
import json

def GetResponse(url, data):
    headers = {
        # Cookie 用户信息，常用于检测是否登录账号
        "Cookie": "LIVE_BUVID=AUTO3916337924675559; buvid_fp_plain=undefined; DedeUserID=10786395; DedeUserID__ckMd5=fb6124d0f2f7ec49; buvid4=7D2102E5-7F8A-94D3-18F6-3D54A450384133572-022020416-fy711ESOQ27v%2F7lyyytRKw%3D%3D; hit-new-style-dyn=1; rpdid=|(m)ml|~uRm0J'u~|JkY)Yum; FEED_LIVE_VERSION=V_WATCHLATER_PIP_WINDOW3; PVID=1; hit-dyn-v2=1; fingerprint=1014f7ceb9fad878a9e731e8fdfd8343; enable_web_push=DISABLE; buvid3=4B08942C-FC73-751E-6AA3-27D15872E02082788infoc; b_nut=1719071382; header_theme_version=CLOSE; _uuid=9FDB2FBE-3596-A5CB-B4D3-ABDEE389DD5E26880infoc; CURRENT_FNVAL=4048; CURRENT_QUALITY=80; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjE4MzQyMjIsImlhdCI6MTcyMTU3NDk2MiwicGx0IjotMX0.heM5wFlUB-LE7Ok6WDiDHHfykBQodg5Neghy13sOPTw; bili_ticket_expires=1721834162; buvid_fp=1014f7ceb9fad878a9e731e8fdfd8343; SESSDATA=184c7674%2C1737297433%2C53c03%2A72CjDhRyMQ2LpwXN_BxO6ceAwBKgtYqEHKjrCpU4o8OXQwxTqcl34bnAY0WKxqhGFz2MASVmZ5VGxtMXNDVXl6Q250TDNXc0I0a1FpRF8yY3JaMmdaamxzN2hsZEhrU3lrSUpWRF8xeDJCbkJKQjE0S3Y0dkhiaTEyS0ZHTElzNGNPRk9OWUsxRHNBIIEC; bili_jct=46494f7b5befe5d8dc7dd74a2c5fb121; sid=5uo7m2ax; home_feed_column=4; browser_resolution=1178-550; bp_t_offset_10786395=957563688787640320; b_lsid=33391C1010_190E2B35CDE",
        # User-Agent 用户代理, 表示浏览器/设备基本身份信息
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    response = requests.get(url=url, params=data, headers=headers)
    return response


def GetContent(date, NextPage, w_rid):
    # 请求网址
    link = 'https://api.bilibili.com/x/v2/reply/wbi/main'
    # 查询参数
    params = {
        'oid': '890808562',
        'type': '1',
        'mode': '2',
        'pagination_str':'{"offset":%s}' % NextPage,
        'plat': '1',
        'web_location': '1315875',
        'w_rid': w_rid,         # 加密参数
        'wts': date,            # 时间戳
        # 从热评开始：
        # 'oid': '890808562',
        # 'type': '1',
        # 'mode': '3',
        # 'pagination_str':'{"offset":%s}' % NextPage,
        # 'plat': '1',
        # 'web_location': '1315875',
        # 'w_rid': w_rid,        
        # 'wts': date,            
    }
    # 调用函数发送请求
    response = GetResponse(url=link, data=params)
    # 获取响应json数据内容
    JsonData = response.json()
    # 提取评论数据所在列表replies
    replies = JsonData['data']['replies']

    info_list = []
    for index in replies:
        try:
            dit = {
                '昵称': index['member']['uname'],
                '性别': index['member']['sex'],
                # '地区': index['reply_control']['location'].replace('IP属地：', ''),
                '评论': index['content']['message'],
            }
            # print(dit)
            info_list.append(dit)
        except:
            pass

    # 获取下一页的参数内容
    next_offset = JsonData['data']['cursor']['pagination_reply']['next_offset']
    offset = json.dumps(next_offset)
    # 返回数据内容
    return info_list, offset


def Hash(date, NextPage):
    next_offset = '{"offset":%s}' % NextPage
    pagination_str = quote(next_offset) # 编码转换

    # 获取w_rid值：md5(L+z), z='ea1db124af3c7062474693fa704f4ff8'
    ee = [
        "mode=2",
        # "mode=3",
        "oid=890808562",
        f"pagination_str={pagination_str}",
        "plat=1",
        "type=1",
        "web_location=1315875",
        f"wts={date}",
    ]
    L = '&'.join(ee)
    string = L + 'ea1db124af3c7062474693fa704f4ff8'
    # md5加密
    MD5 = hashlib.md5()
    MD5.update(string.encode('utf-8'))
    w_rid = MD5.hexdigest()

    # print('w_rid: ' + w_rid)
    return w_rid


if __name__ == '__main__':
    f = open('data.csv', mode='w', encoding='utf-8', newline='')
    # csv_writer = csv.DictWriter(f, fieldnames=['昵称', '性别', '地区', '评论'])
    csv_writer = csv.DictWriter(f, fieldnames=['昵称', '性别', '评论'])
    csv_writer.writeheader()

    # 定义第一页参数
    NextPage = '""'
    while True:
        try:
            # 获取当前时间戳
            date = int(time.time())
            # 获取加密参数
            w_rid = Hash(date=date, NextPage=NextPage)

            # 获取数据内容
            info_list, NextPage = GetContent(date, NextPage, w_rid)
            print('NextPage: ' + NextPage)
            
            # 写入数据
            for info in info_list:
                csv_writer.writerow(info)
        except:
            break
