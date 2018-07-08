# -*- coding: utf-8 -*-

import re
# f = lambda x:True if x.startswith("https")  else False
f = lambda x: x.startswith("https")

if __name__ == "__main__":
    #

    str = "https://www.zhihu.com/question/283002292"
    # str = "https://www.zhihu.com/question/283002292/answer/428663049"
    match_obj = re.match("(.*zhihu.com/question/(\d+)).*", str)
    if match_obj:
        print("group1:" , match_obj.group(1))
        print("group2:" , match_obj.group(2))

