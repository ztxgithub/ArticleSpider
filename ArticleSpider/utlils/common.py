# -*- coding: utf-8 -*-
import hashlib

def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    md5 = hashlib.md5()
    md5.update(url)
    return md5.hexdigest()

if __name__ == "__main__":
    print(get_md5("https://www.baidu.com"))

