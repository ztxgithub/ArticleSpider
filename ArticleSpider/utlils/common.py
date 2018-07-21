# -*- coding: utf-8 -*-
import hashlib
import re

def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    md5 = hashlib.md5()
    md5.update(url)
    return md5.hexdigest()

"""
    通过正则表达式从字符串提取出数字
"""
def extract_num(text):
    match_var = re.match(r'.*?(\d+).*', text)
    if match_var:
        num = int(match_var.group(1))
    else:
        num = 0
    return num

if __name__ == "__main__":
    print(get_md5("https://www.baidu.com"))

