# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from datetime import datetime
import scrapy

# MapCompose类可以将我们对item调用任何多的函数，主要解决对item中各个字段进行处理
# TakeFirst 类 主要取list数组中的第一个元素
from scrapy.loader.processors import MapCompose,TakeFirst,Join

# 对于自定义ArticleItemLoader类的重载
from scrapy.loader import ItemLoader

# 正则表达式
import re

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 这里的参数 value 实际上是 title 传来的值
def add_jobbole(value):
    return  value + " "


def date_convert(value):
    try:
        create_date = datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.now().date()

    return create_date

def get_nums(value):
    match_var = re.match(r'.*?(\d+).*', value)
    if match_var:
        num = int(match_var.group(1))
    else:
        num = 0
    return num

def return_value(value):
    return value

## 为了不需要对每一个item字段都进行output_processor = TakeFirst(),我们可以自己定义itemLoader
class ArticleItemLoader(ItemLoader):
    #自定义ItemLoader
    ## 实际上只取list第一个元素
    default_output_processor = TakeFirst()

# 这个JobBoleArticleItem达到了对代码的重用
class JobBoleArticleItem(scrapy.Item):

    # input_processor 含义是 当 item 的 title字段的值传递进来的时候，可以对传递进来的值进行预处理
    # MapCompose 函数 可以传入多个函数变量
    title = scrapy.Field(
        input_processor = MapCompose(add_jobbole, lambda x:x + " ")
    )             # 标题
    datetime = scrapy.Field(
        input_processor=MapCompose(date_convert),
        # ## 实际上只取list第一个元素
        # output_processor = TakeFirst()  # 因为自定义了 ArticleItemLoader
    )          # 发表日期
    like_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )          # 点赞数
    url = scrapy.Field()               # 对应的url
    url_object_id = scrapy.Field()      # 对应的url的md5
    front_image_url = scrapy.Field(
        # 这里必须为list,重载output_processor覆盖默认的default_output_processor
        #
        output_processor=MapCompose(return_value)
    )   # 存放文章封面图
    front_image_path = scrapy.Field()  # 存放文章封面图的本地路径
    collect_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )       # 收藏数

    context = scrapy.Field()           # 正文





"""
    知乎业务代码
"""

"""
    知乎的问题 item
"""
class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    """
        由于 create_time 和 update_time 在网页上获取不到不写 
    """
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_tiem = scrapy.Field()


"""
    知乎的问题回答 item
"""
class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
