# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
##这个adbapi能够将我们的数据库操作变为异步化的操作
from twisted.enterprise import adbapi

import MySQLdb
import MySQLdb.cursors

# 进行数据库的保存
class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

# 自定义保存json文件
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding="utf-8")
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        #下一个pipeline要处理,所以要return item
        return item
    ## 当出了作用域,自动调用spider_closed进行文件关闭
    def spider_closed(self, spider):
        self.file.close()

class JsonExporterPipeline(object):
    # 调用scrapy提供的json exporter 导出json文件
    def __init__(self):
        self.file = open("article_exporter.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

#进行item中其他项的赋值
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for status, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item

#将数据同步得保存到数据库中
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1', user='root', password='123456',
                                    database='article_spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, datetime, url, 
            url_object_id, front_image_url, front_image_path, like_num, collect_num, context)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        self.cursor.execute(insert_sql, (item["title"], item["datetime"], item["url"],
                                         item["url_object_id"], item["front_image_url"],
                                         item["front_image_path"], item["like_num"],
                                         item["collect_num"], item["context"]))
        self.conn.commit()


#通过twisted框架进行数据库插入(异步得插入到数据库中)
"""
    通过 MysqlTwistedPipeline() 来处理所有的各个类型的 item, 例如 伯乐在线的item,
    知乎 question_item, 知乎 answer_item
"""
class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings): # 这里的 settings 就是对应于 settings.py 中 相关的数据库参数
        # dict 里面的参数名称 例如 ”database"这些要与MySQLdb.connect函数中的固定参数名要一致
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            database=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )

        ## twisted 本身使用时异步的容器，具体操作还是对应的数据库
        ## "MySQLdb" 对应于 数据库的模块名
        ## *connargs 是数据库连接的参数
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)

    # 使用twisted将mysql插入变为异步执行
    def process_item(self, item, spider):
        # 调用twisted 中的runInteraction函数来执行异步操作
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 进行错误的处理判断
        query.addErrback(self.handle_error, item)

    """
        这个函数非常重要,在正式投入使用时, 我们通过将错误信息插入到日志中，
        有时候插入失败 以及 代码有 bug, 这时错误信息就非常关键,
        通过打断点进行代码调试
    """
    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):

        """
            根据不同的 item 构建不同的 sql 语句并插入到 MySQL 中
        """

        # if item.__class__.__name__ == "JobBoleArticleItem": # 这种硬编码的方式,在后续修改的时候比较麻烦
        #     #执行具体得插入
        #     insert_sql = """
        #                 insert into jobbole_article(title, datetime, url,
        #                 url_object_id, front_image_url, front_image_path, like_num, collect_num, context)
        #                 values(%s, %s, %s, %s, %s, %s, %s, %s, %s);
        #             """
        #
        #     cursor.execute(insert_sql, (item["title"], item["datetime"], item["url"],
        #                                      item["url_object_id"], item["front_image_url"],
        #                                      item["front_image_path"], item["like_num"],
        #                                      item["collect_num"], item["context"]))

        """
            这样只需要在各自的 item 中写好 各种的 SQL 语句就行了,
            这个方法体现了 面向对象编程
        """
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql,params)

        # 不需要commit twisted自动帮我们commit
