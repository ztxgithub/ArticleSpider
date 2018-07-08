# -*- coding: utf-8 -*-
import scrapy
import re
import json

"""
  这是兼容 python2(urlparse) 和 python3的做法
"""
try:
    import urlparse as parse
except:
    from urllib import parse


user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)" \
             " AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/63.0.3239.108 Safari/537.36"
headers = {
    "HOST":"www.zhihu.com",
    "Referer":"https://www.zhihu.com",
    "User-Agent":user_agent
}

# 要爬取知乎,而且知乎一定要先登录,

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    def parse(self, response):

        """
        提取出 html 页面中的所有 url 并跟踪这些 url 进一步的爬取
        如果提取的 url 中的格式为 /question/xxx 就下载之后直接进入解析函数
        """

        """
            所有的 url 链接都是放在 a 标签中，提取出属性值为 href 的,
            例如 <a target="_blank"  href="/question/282549893/answer/427290578">
            注意到该 href 不是绝对的 url
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        """
        需要将all_urls中的javascript过滤掉
        """
        all_urls = filter(lambda x:x.startswith("https"), all_urls)
        for url in all_urls:
            """
            需要对 url 中 包含 question 字符串进行筛选
            我们需要从 https://www.zhihu.com/question/283002292/answer/428663049"
            中提取去 question_id(283002292), 以及得到 https://www.zhihu.com/question/283002292 字段
            需要考虑2种情况
                (1) https://www.zhihu.com/question/283002292
                (2) https://www.zhihu.com/question/283002292/answer/428663049
            """
            match_obj = re.match(".*zhihu.com/question/(\d+)($|/).*", url)
            if match_obj:
                """
                嵌套匹配,则由父的为1 
                """
                request_url = match_obj.group(1)  # https://www.zhihu.com/question/283002292
                question_id = match_obj.group(2)

                """
                在 scrapy 中是通过 yield 异步将参数调给下载器，这边一定要是scrapy.Request()对象，
                这个对象传递出去才能被下载器执行
                
                """
                yield scrapy.Request(request_url, headers=headers, callback=self.parse_question)

    """
        处理 question 页面,从页面中提取具体得 question item
    """
    def parse_question(self, response):
        """
              处理新版本，在调试(F12)过程中,title实际上放在class 为 QuestionHeader-title中
              <h1 class="QuestionHeader-title">你是如何自学 Python 的？</h1>
        """

        """
            采用itemLoader方法进行解析使得代码更加简洁
        """
        if "QuestionHeader-title" in response.text:

            pass
        else:
            """
                处理知乎旧版本
            """


    # 在调用parse之前先调用 start_requests()
    # 先完成用户的登录
    def start_requests(self):
        #通过scrapy的Request获取get_xsrf,这个scrapy.Request是异步的,要设置回调函数
        # 如果我们不显式传入callback,则scrapy默认调用 parse
        return [scrapy.Request('https://www.zhihu.com/signup?next=%2Finbox',
                               headers = headers, # 只要向知乎进行数据请求都要 指明headers
                               callback=self.login)]

    def login(self, response):
        response_text = response.text
        # 默认情况下正则表达式是匹配全文的一行
        #如果要匹配范围为全文,则增加传入的参数 re.DOTALL
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf_value = ''
        if match_obj:
            xsrf_value = (match_obj.group(1))

        if xsrf_value:
            post_url = "https://www.zhihu.com/login/phone_num"

            # 需要向该post_url 传递的数据
            post_data = {
                "_xsrf":xsrf_value,
                "phone_num": "15963214598",  # 填写对应的手机号
                "password": "password"
            }

            # scrapy.FormRequest可以提供表单的提交
            # 这里的每一个FormRequest都要设置callback,因为scrapy是基于twisted框架的,是异步的
            return [scrapy.FormRequest(
                url = post_url,
                formdata = post_data,
                headers = headers, # 只要向知乎进行数据请求都要 指明headers
                callback=self.check_login
            )]

    def check_login(self, response):
        #判断服务器的返回数据是否成功
        text_json = json.load(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            # 这部分内容是原来scrapy的start_requests()方法实现内容
            # 下面是start_requests()方法老的实现内容,因为每个向知乎交互数据其headers都要是 浏览器等信息
            # 所以要重写 make_requests_from_url
            # for url in self.start_urls:
            #     yield self.make_requests_from_url(url)

            for url in self.start_urls:
                # 如果不写回调函数,则scrapy会默认调用 ZhihuSpider.parse
                yield scrapy.Request(url, dont_filter=True, headers = headers)
        pass




