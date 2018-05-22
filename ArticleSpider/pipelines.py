# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter

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
        for status, value in results:
            image_file_path = value["path"]

        item["front_image_path"] = image_file_path
        return item