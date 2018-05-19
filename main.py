# -*- coding: utf-8 -*-

from scrapy.cmdline import execute  #用于调试代码
import sys
import os
# os.path.abspath(__file__) 获取到main.py所在的绝对路径
# 获取该项目的绝对路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#调用execute来执行scrapy
#在cmd 中也是执行 cmd> scrapy crawl jobbole
#这个时候就可以在jobbole.py进行断电调试
#这个时候可以要将 settings.py 中的 置为ROBOTSTXT_OBEY = False，因为在scrapy运行时默认是true，将网站中遵从robots.txt，将
#不合理的url过滤掉
execute(["scrapy", "crawl", "jobbole"])