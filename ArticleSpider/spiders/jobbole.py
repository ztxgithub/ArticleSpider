# -*- coding: utf-8 -*-
import scrapy
import re

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/114000/']

    def parse(self, response):
        # re_selector = response.xpath('//*[@id="post-114000"]/div[1]/h1/text()')
        # re_selector = response.xpath('//*[@id="post-114000"]/div[1]/h1')
        # re_selector2 = response.xpath('//div[@class="entry-header"]/h1/text()')
        title =  response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        datetime = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip()
        like_num = int(response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0])
        collect_text = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        match_var = re.match(r'.*(/d+).*', collect_text)
        if match_var:
            collect_num = match_var.group(1)

        comment_text = response.xpath("//a[@href='#article-comment']/span[1]/text()").extract()[0]
        match_var = re.match(r'.*(/d+).*', comment_text)
        if match_var:
            comment_num = match_var.group(1)

        context = response.xpath("//div[@class='entry']").extract()[0]
        pass

