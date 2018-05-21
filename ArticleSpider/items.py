# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()             # 标题
    datetime = scrapy.Field()          # 发表日期
    like_num = scrapy.Field()          # 点赞数
    url = scrapy.Field()               # 对应的url
    url_object_id = scrapy.Field()      # 对应的url的md5
    front_image_url = scrapy.Field()   # 存放文章封面图
    front_image_path = scrapy.Field()  # 存放文章封面图的本地路径
    collect_num = scrapy.Field()       # 收藏数
    context = scrapy.Field()           # 正文