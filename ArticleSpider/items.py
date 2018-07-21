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
from ArticleSpider.utlils.common import extract_num
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

from w3lib.html import remove_tags

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
        在这个定义只关于 JobBoleArticleItem 特定的 SQL语句,
        把SQL语句的构建 放到具体某个 item 中来, 这样就不用将 这些变化的 SQL
        放到 pipeline中去,
    """
    def get_insert_sql(self):
        insert_sql = """
                               insert into jobbole_article(title, datetime, url, 
                               url_object_id, front_image_url, front_image_path, like_num, collect_num, context)
                               values(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                               ON DUPLICATE KEY UPDATE context=values(context),
                               like_num=values(like_num), collect_num=values(collect_num);
                    """

        """
           构建 tuple(元组)
        """
        params = (self["title"], self["datetime"], self["url"],
                  self["url_object_id"], self["front_image_url"],
                  self["front_image_path"], self["like_num"],
                  self["collect_num"], self["context"])

        return insert_sql,params





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
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    """
        在这个定义 关于 ZhihuQuestionItem 的 insert SQL 的语句
        这样在 pipeline 中 进行数据库的插入, 则不需要判断是哪一个 item
    """
    def get_insert_sql(self):
        insert_sql = """
                               insert into zhihu_question(zhihu_id, topics, url, 
                               title, content, answer_num, comments_num, 
                               watch_user_num, click_num, crawl_time)
                               values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                              ON DUPLICATE KEY UPDATE content=values(content),
                               comments_num=values(comments_num), answer_num=values(answer_num),
                               watch_user_num=values(watch_user_num) 
                               click_num=values(click_num);
                           """
        """
           这里 ZhihuQuestionItem中 采用 item_Loader, 则每一个 item 都是一个 list,
           需要将 list 转化为单个的值,提供有别于 JobBoleArticleItem 中的处理方式
        """
        zhihu_id = int("".join(self["zhihu_id"]))
        topics = ",".join(self["topics"])
        """
            也可以用 url = self["url"][0]
        """
        url = "".join(self["url"])
        title = "".join(self["title"])
        content = "".join(self["content"])
        """
            先转化为 answer_num 字符串, 
            再从 answer_num 字符串进行提取数字
        """
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))
        watch_user_num = extract_num("".join(self["watch_user_num"]))
        click_num = extract_num("".join(self["click_num"]))
        crawl_time = datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content,
                  answer_num, comments_num, watch_user_num,
                  click_num, crawl_time)

        return insert_sql,params

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


    """
        在这个定义 关于 ZhihuAnswerItem 的 insert SQL 的语句
        这样在 pipeline 中 进行数据库的插入, 则不需要判断是哪一个 item
    """
    def get_insert_sql(self):
        """
            当数据库中出现插入冲突(主键相同),使用 MySQL 特有的语句 使得
            主键不动, 只更新指定的字段
        """
        insert_sql = """
                               insert into zhihu_answer(zhihu_id, url, 
                               question_id, author_id, content, praise_num, 
                               comments_num, create_time, update_time,
                               crawl_time) 
                               values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                               ON DUPLICATE KEY UPDATE content=values(content),
                               comments_num=values(comments_num), praise_num=values(praise_num),
                               update_time=values(update_time);
                      """
        """
            因为 answer_item 不是通过 itemLoader 从网页上进行 item_Loader.add_css,
            item_Loader.add_value 等方法提取, 而是直接通过 answer_item["zhihu_id"]提取
            所以 self["zhihu_id"] 就不是 list 类型
        """

        create_datetime = datetime.fromtimestamp(self["create_time"])
        update_datetime = datetime.fromtimestamp(self["update_time"])
        params = (
            self["zhihu_id"], self["url"], self["question_id"], self["author_id"],
            self["content"], self["praise_num"], self["comments_num"],
            create_datetime.strftime(SQL_DATETIME_FORMAT),
            update_datetime.strftime(SQL_DATETIME_FORMAT),
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT)
        )

        return insert_sql, params




def remove_splash(value):
    # 去掉工作城市的斜线
    return value.replace("/", "")


def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years_min = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years_max = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary_min, salary_max, job_city, work_years_min, work_years_max, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary_min=VALUES(salary_min), salary_max=VALUES(salary_max), job_desc=VALUES(job_desc)
        """

        match_obj1 = re.match("经验(\d+)-(\d+)年", self['work_years_min'])
        match_obj2 = re.match("经验应届毕业生", self['work_years_min'])
        match_obj3 = re.match("经验不限", self['work_years_min'])
        match_obj4 = re.match("经验(\d+)年以下", self['work_years_min'])
        match_obj5 = re.match("经验(\d+)年以上", self['work_years_min'])

        if match_obj1:
            self['work_years_min'] = match_obj1.group(1)
            self['work_years_max'] = match_obj1.group(2)
        elif match_obj2:
            self['work_years_min'] = 0.5
            self['work_years_max'] = 0.5
        elif match_obj3:
            self['work_years_min'] = 0
            self['work_years_max'] = 0
        elif match_obj4:
            self['work_years_min'] = 0
            self['work_years_max'] = match_obj4.group(1)
        elif match_obj5:
            self['work_years_min'] = match_obj4.group(1)
            self['work_years_max'] = match_obj4.group(1) + 100
        else:
            self['work_years_min'] = 999
            self['work_years_max'] = 999

        match_salary = re.match("(\d+)[Kk]-(\d+)[Kk]", self['salary_min'])
        if match_salary:
            self['salary_min'] = match_salary.group(1)
            self['salary_max'] = match_salary.group(2)
        else:
            self['salary_min'] = 666
            self['salary_max'] = 666
        match_time1 = re.match("(\d+):(\d+).*", self["publish_time"])
        match_time2 = re.match("(\d+)天前.*", self["publish_time"])
        match_time3 = re.match("(\d+)-(\d+)-(\d+)", self["publish_time"])
        if match_time1:
            today = datetime.datetime.now()
            hour = int(match_time1.group(1))
            minutues = int(match_time1.group(2))
            time = datetime.datetime(
                today.year, today.month, today.day, hour, minutues)
            self["publish_time"] = time.strftime(SQL_DATETIME_FORMAT)
        elif match_time2:
            days_ago = int(match_time2.group(1))
            today = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            self["publish_time"] = today.strftime(SQL_DATETIME_FORMAT)
        elif match_time3:
            year = int(match_time3.group(1))
            month = int(match_time3.group(2))
            day = int(match_time3.group(3))
            today = datetime.datetime(year, month, day)
            self["publish_time"] = today.strftime(SQL_DATETIME_FORMAT)
        else:
            self["publish_time"] = datetime.datetime.now(
            ).strftime(SQL_DATETIME_FORMAT)

        params = (
            self["title"],
            self["url"],
            self["url_object_id"],
            self["salary_min"],
            self["salary_max"],
            self["job_city"],
            self["work_years_min"],
            self["work_years_max"],
            self["degree_need"],
            self["job_type"],
            self["publish_time"],
            self["job_advantage"],
            self["job_desc"],
            self["job_addr"],
            self["company_name"],
            self["company_url"],
            self["tags"],
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params