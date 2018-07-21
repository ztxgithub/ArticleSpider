# -*- coding: utf-8 -*-
## 通过requests模块来模拟知乎登录

import requests
# python系统自带的cookies作为参数传入到 requests模块中

# 保证python2 和 python3 的兼容代码
try:
    # python2 是 cookielib
    import cookielib
except:
    # 出现异常则是python3 的环境,将http.cookiejar重命名为 cookielib
    import http.cookiejar as cookielib

import re
import time

#有了这个session后,每次请求就不用requests.get了,session代表的是
#某一次连接
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookies can not load")

user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)" \
             " AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/63.0.3239.108 Safari/537.36"
headers = {
    "HOST":"www.zhihu.com",
    "Referer":"https://www.zhihu.com",
    "User-Agent":user_agent
}

#判断用户是否登录
def is_login():
    # 通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/inbox"
    response = session.get(inbox_url, headers=headers, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True
def get_xsrf():
    # 调用requests模块,向知乎请求数据
    # response = requests.get("https://www.zhihu.com", headers=headers)

    #使用session进行get方法,而不是每次都用requests.get()
    response = session.get("https://www.zhihu.com", headers=headers)
    # 通过 response.text 得到服务器响应的数据,在经过正则匹配
    print("get_xsrf")
    print(response.text)

    # 从 response.text 中提取出对应_xsrf的值
    # text = '<input type="hidden" name="_xsrf" value="1111123121">'

    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        return (match_obj.group(1))
    else:
        return ""

def get_index():
    response = session.get("https://www.zhihu.com", headers=headers)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")

"""
    获取验证码
"""
def get_captcha():
    """
        先提供一个根据时间戳的字符串
    """
    t = str(int(time.time() * 1000))

    # 构造请求 验证码的 url
    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)

    response = session.get(captcha_url, headers=headers)
    # 以二进制的格式打开 验证码图片
    with open("captcha.jpg", "wb") as f:
        f.write(response.content)

    from PIL import Image
    try:
        im = Image.open("captcha.jpg")
        im.show()
        im.close()
    except:
        pass

    """
        这边显示验证码的图片,需要用户进行对话框输入
    """
    captcha_value = input("imput captcha\n >")
    return captcha_value


# 进行知乎的登录注册(旧版的接口)
def zhihu_old_login(account, password):

    if re.match("^1\d{10}", account):
        # 如果是手机号码登陆则，url
        post_url = "https://www.zhihu.com/login/phone_num"

        """
            在向登录url. post登录数据前, 要先请求登录验证码
        """
        captcha_value = get_captcha()
        """
            需要向该post_url 传递的数据,
            其中包括传递验证码
        """
        post_data = {
            "_xsrf":get_xsrf(),
            "phone_num":account,
            "password":password,
            "captcha":captcha_value  # 验证码
        }

        # 模拟登录就是将数据内容post到某个url中
        # response = requests.post(post_url, data = post_data, headers=headers)

        # 模拟登录这里利用的requests模块的session
        # 使用session进行post 方法,而不是每次都用requests.post()
        response_text = session.post(post_url, data = post_data, headers=headers)

        #将服务器返回的cookies保存到本地,这样以后就不再需要调用zhihu_old_login方法,
        #因为已经保存了session
        session.cookies.save()

    else: #邮箱的登录方式
        if "@" in account:
            post_url = "https://www.zhihu.com/login/email"

            # 需要向该post_url 传递的数据
            post_data = {
                "_xsrf": get_xsrf(),
                "email": account,
                "password": password
            }
            response_text = session.post(post_url, data=post_data, headers=headers)
            session.cookies.save()


if __name__ == "__main__":
    get_captcha()
