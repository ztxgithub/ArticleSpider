# -*- coding: utf-8 -*-

import requests
import json

class YDMHttp(object):
    apiurl = 'http://api.yundama.com/api.php'
    username = '' # 云打码付费用户的账号
    password = '' # 云打码付费用户的用户名
    appid = ''    # 云打码开发者中软件代码
    appkey = ''   # 云打码开发者中的通讯密钥

    def __init__(self, username, password, appid, appkey):
        self.username = username
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def balance(self):
        data = {'method': 'balance', 'username':self.username,
                'password':self.password, 'appid': self.appid,
                'appkey':self.appkey}
        response_data = requests.post(self.apiurl, data=data)
        ret_data = json.loads(response_data.text)
        """
            ret_data["ret"] 为 0 则获取积分成功
        """
        if ret_data["ret"] == 0:
            print("获取剩余积分", ret_data["balance"])
            return ret_data["balance"]
        else:
            return None

    def login(self):
        data = {'method': 'login', 'username': self.username,
                'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response_data = requests.post(self.apiurl, data=data)
        ret_data = json.loads(response_data.text)
        """
            ret_data["ret"] 为 0 则登录成功
        """
        if ret_data["ret"] == 0:
            print("登录成功", ret_data["uid"])
            return ret_data["uid"]
        else:
            return None


    """
        进行验证码的识别
        其中 codetype ：代表验证码是什么类型的，例如 是 4 位字母的
    """
    def decode(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username,
                'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype),
                'timeout': str(timeout)}
        files = {'file': open(filename, 'rb')}
        response_data = requests.post(self.apiurl, files=files, data=data)
        ret_data = json.loads(response_data.text)
        """
            ret_data["ret"] 为 0 则验证码的识别成功
        """
        if ret_data["ret"] == 0:
            print("验证码的识别成功", ret_data["text"])
            return ret_data["text"]
        else:
            return None



if __name__ == "__main__":
    #用户名
    username = 'xxxx'
    password = 'xxxx'  # 云打码付费用户的用户名
    appid = 'xxxxx'  # 云打码开发者中软件代码
    appkey = 'xxxx'  # 云打码开发者中的通讯密钥
    verification_request = YDMHttp()