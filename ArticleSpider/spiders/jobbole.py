# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime

from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utlils.common import get_md5
import hashlib

from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页的文章url并交给scrapy下载，通过解析函数进行具体字段的解析
        2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        """

        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            ## 其中post_url为绝对路径 http://blog.jobbole.com/110287/
            ## 有的网站提取的post_url为110287/，则需要通过 response.url + post_url
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url,post_url), meta={"front_image_url":image_url}, callback=self.parse_detail)

        #提取下一页并交给scrapy进行下载
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_urls:
            yield Request(url=parse.urljoin(response.url,next_urls), callback=self.parse)
    def parse_detail(self, response):
        article_item = JobBoleArticleItem()
        ## 提取文章的具体字段
        ## xpath的提取元素的用法
        # re_selector = response.xpath('//*[@id="post-114000"]/div[1]/h1/text()')
        # re_selector = response.xpath('//*[@id="post-114000"]/div[1]/h1')
        # re_selector2 = response.xpath('//div[@class="entry-header"]/h1/text()')
        # title =  response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # datetime = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip()
        # like_num = int(response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0])
        #
        # collect_text = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        # match_var = re.match(r'.*?(\d+).*', collect_text)
        # if match_var:
        #     collect_num = match_var.group(1)
        #
        # comment_text = response.xpath("//a[@href='#article-comment']/span[1]/text()").extract()[0]
        # match_var = re.match(r'.*?(\d+).*', comment_text)
        # if match_var:
        #     comment_num = match_var.group(1)
        #
        # context = response.xpath("//div[@class='entry']").extract()[0]

        ## css选择器提取元素的用法
        # front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        # title_css = response.css(".entry-header h1::text").extract()[0]
        # datetime_css = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip()
        # like_num_css = int(response.css(".vote-post-up h10::text").extract()[0])
        #
        # collect_text_css = response.css(".bookmark-btn::text").extract()[0]
        # match_var = re.match(r'.*?(\d+).*', collect_text_css)
        # if match_var:
        #     collect_num_css = match_var.group(1)
        #
        # comment_text_css = response.css("a[href='#article-comment'] span::text").extract()[0]
        # match_var = re.match(r'.*?(\d+).*', comment_text_css)
        # if match_var:
        #     comment_num_css = match_var.group(1)
        #
        # context_css = response.css(".entry").extract()[0]
        #
        # article_item["title"] = title_css
        # # datetime_css = "2018/05/12"
        # try:
        #     create_date = datetime.strptime(datetime_css, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.now().date()
        # article_item["datetime"] = create_date
        # article_item["like_num"] = like_num_css
        # article_item["url"] = response.url
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["front_image_url"] = [front_image_url]
        # article_item["collect_num"] = collect_num_css
        # article_item["context"] = context_css

        # 通过item Loader 来加载 item
        # 首先定义itemLoader 的实例
        # ItemLoader()函数有2个重要的参数
        # 第一个参数 item对应于  items.py中的JobBoleArticleItem()
        # 第二个参数是 response

        # 为了能够自动取list的第一个元素,我们自定义了ArticleItemLoader 继承 ItemLoader
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)

        #item_loader.add_css() 是通过网页中的样式进行提取,为 item_loader添加规则
        # 用add_css()方法的好处是 其代码较为清晰,并且参数css的样式可以通过对数据库查找动态的加载,而
        # 不是硬编码到程序中，方便进行动态配置
        # 第一个参数为item中 选项值
        # 第二个参数为css的样式
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("context", ".entry")
        item_loader.add_css("datetime", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_css("like_num", ".vote-post-up h10::text")
        item_loader.add_css("collect_num", ".bookmark-btn::text")
        item_loader.add_css("context", ".entry")

        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        # 如果不是通过css的样式取出对应的值,则使用 item_loader.add_value
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])

        # 调用 load_item() 方法,才会将 前面的规则进行解析
        article_item = item_loader.load_item()


        yield article_item

