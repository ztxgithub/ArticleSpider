# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
from tools.crawl_cixi_ip import GetIP
from selenium import webdriver
from scrapy.http import HtmlResponse

class JSPageMiddleware(object):

    # 这样可以使得不打开很多浏览器
    def __init__(self):
        self.browser = webdriver.Chrome(
            executable_path="C:/spiderDriver/chromedriver.exe")
        super(JSPageMiddleware, self).__init__()

    # 通过chrome请求动态网页
    def process_request(self, request, spider):
        if spider.name == "jobbole":
            self.browser.get(request.url)
            import time
            time.sleep(3)
            print ("访问:{0}".format(request.url))

            """
                通过 Selenium 已经向网站请求页面
                了，就不需要再通过下载器进行二次下载了
                scrapy 一旦遇到 HtmlResponse，就不会用下载器
                下载页面，而是直接返回
            """
            return HtmlResponse(
                url=self.browser.current_url,
                body=self.browser.page_source,
                encoding="utf-8",
                request=request)

class ArticlespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ArticlespiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

"""
   随机更换 User-agent
"""

class RandomUserAgentMiddleware(object):

    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        """
            定义第三方模块 UserAgent对象, 
            通过调用 self.ua.random 方法取随机浏览器的User-agent
            通过调用 self.ua.google 方法去google浏览器的随机User-agent
        """
        self.ua = UserAgent()
        """
           通过 crawler 对象可以从 setting.py文件中取一些定义的参数
        """
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    """
     将 crawler 对象传递到 RandomUserAgentMiddleware类中
    """
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        """
            通过 getattr()方法 得到
            self.ua.random,self.ua.google 这取决于 self.ua_type 的值
        """
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault('User-Agent', get_ua())
        """
            设置 ip 代理, 隐藏本机的 ip,不会被服务器封
        """
        request.meta["proxy"] = "http://125.118.247.4:6666"

class RandomProxyMiddleware(object):
    # 动态设置 ip 代理
    def process_request(self, request, spider):
        get_ip = GetIP()
        request.meta["proxy"] = get_ip.get_random_ip()


