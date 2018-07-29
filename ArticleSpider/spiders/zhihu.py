# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time

from datetime import datetime

from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem, ZhihuQuestionItem
from ArticleSpider.settings import user_agent_list

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

import random

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

    """
        question的 第一页 answer的请求 url,
        通过在知乎上, 按 F12, 点击 查看全部XXX回答, 在 Network 标签中取到
    """
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={1}&limit={2}&sort_by=default"

    # 通过对 custom_settings 的设置，可以覆盖掉 settings.py 默认的配置
    custom_settings = {
        "COOKIES_ENABLED":True
    }

    def parse(self, response):

        """
            随机更换user_agent：
                构造随机数
        """
        random_index = random.randint(0, len(user_agent_list) - 1)
        random_agent = user_agent_list[random_index]

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
            match_obj = re.match("(.*zhihu.com/question/(\d+))($|/).*", url)
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

            else:
                """
                    如果该 url 不满足要提取的 question, 则继续向该 url 进行深度优先请求
                """
                yield scrapy.Request(url, headers=headers, callback=self.parse)

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

            item_Loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            """
                有2中方法可以取到 zhihu_id 
                    第一种: 直接在 response.url 进行正则表达式匹配
                    第二种: 在 parse函数中, 已经解析出 question_id, 只需要 
                            yield scrapy.Request(request_url,meta={"question_id":question_id},
                                                headers=headers, callback=self.parse_question)
                                                
                            在 parse_question 函数中 
                                    question_id = int(response.meta.get("question_id", ""))
                        
            """
            match_obj = re.match("(.*zhihu.com/question/(\d+))($|/).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))


            item_Loader.add_value("zhihu_id", question_id)

            item_Loader.add_css("title", ".QuestionHeader-title::text")
            """
                这边只是提取出唯一的大范围
                 <div class="QuestionHeader-detail">
                        <div class="QuestionRichText QuestionRichText--expandable">
                            <div>
                            <span class="RichText ztext" itemprop="text">
                                <p>Python 的岗位本来就比较少，而且大部分都对经验要求比较高，没有什么初级岗位啊</p>
                                <p>我说的学Python当然不只是学语言，既然说的是学Python入IT坑，
                                    入坑当然是学全套，但我个人认为很多人学完全套还是找不到工作的，
                                    尤其是非北上广城市，职位数量少，要求反而比一线城市更高，
                                    我个人对这些人转行不看好，欢迎指正。
                                </p>
                                <p></p>
                                </span>
                            </div>
                        </div>
                </div>
                后续提取出content 还要通过 ZhihuQuestionItem对象的预处理函数(input_processor)
            """
            item_Loader.add_css("content", ".QuestionHeader-detail")

            item_Loader.add_value("url", response.url)
            item_Loader.add_css("answer_num", ".QuestionMainAction::text")
            item_Loader.add_css("comments_num", ".QuestionHeader-Comment button::text")

            """
                watch_user_num: 关注者数量, 用 class == NumberBoard-itemValue 取出来的是一个 list
                <div class="NumberBoard-itemName">关注者</div>
                <strong class="NumberBoard-itemValue" title="2895">2,895</strong>
                
                <div class="NumberBoard-itemName">被浏览</div>
                <strong class="NumberBoard-itemValue" title="1778006">1,778,006</strong>
                
                一个是关注者的值, 一个是被浏览的次数
            """
            item_Loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
            item_Loader.add_css("topics", "QuestionHeader-tags .Popover div::text")

            question_item = item_Loader.load_item()
        else:
            """
                处理知乎旧版本
            """

        """
            每解析完新的 question_item 时,就请求 该问题对应的 answer
        """
        yield scrapy.Request(self.start_answer_url.format(question_id, 5, 0),
                             headers=headers,
                             callback=self.parse_answer)
        yield question_item


    """
        处理 question 的 answer 
    """
    def parse_answer(self, response):
        answer_json = json.load(response.text)


        # 解析出该页面是否为最后一个页面
        is_end = answer_json["paging"]["is_end"]
        #总共有多少个回答
        totals = answer_json["paging"]["totals"]
        next_url = answer_json["paging"]["next"]

        """
            在该 url(页面中) 提取 limit 个 anwser
        """
        for answer in answer_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            """
                如果用户在匿名的情况下进行评论的, 是没有id字段的
            """
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None

            """
                可能在回答中 answer["content"] 为 NULL, 但 answer["excerpt] 肯定有
            """
            answer_item["content"] = answer["content"] if "content" in answer else answer["excerpt"]
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.now()

            """
                yield 实际上会交给 pipeline进行进一步的处理
            """
            yield answer_item


        """
            如果 is_end 为 fasle, 说明 还可以请求下一个回答页面
        """
        if not is_end:
            yield scrapy.Request(next_url, headers=headers, callback=self.parse_answer)

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
            # 需要向该post_url 传递的数据
            post_data = {
                "_xsrf":xsrf_value,
                "phone_num": "15963214598",  # 填写对应的手机号
                "password": "password",
                "captcha":""  # 知乎登录验证码
            }


            """
                   先提供一个根据时间戳的字符串
            """
            t = str(int(time.time() * 1000))

            # 构造请求 验证码的 url
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
            """
                在请求验证码的时候无法用 request 模块来请求, 
                现在问题是如何做才能使返回验证码的 response 的 session 与
                scrapy 中 的 response 的 session 一致

                方法: 直接 yield 一个请求图片的 scrapy.request
                      这里面将 scrapy.Request yield 出去会使用同一个 cookies
                      保证  xsrf_value 请求 和 captcha 请求是使用同一个 session
            """
            yield scrapy.Request(captcha_url, headers = headers,
                                 meta={"post_data": post_data},
                                 callback=self.login_after_captcha)

    """
        这里的 response 是请求图片返回的 response
    """
    def login_after_captcha(self, response):

        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/phone_num"
        # 以二进制的格式打开 验证码图片
        with open("captcha.jpg", "wb") as f:
            f.write(response.body) ## 这个地方是放在 response.body 里面

        from PIL import Image
        try:
            im = Image.open("captcha.jpg")
            im.show()
            im.close()
        except:
            pass

        """
            这边显示验证码的图片,需要用户进行对话框输入
        """
        captcha_value = input("imput captcha\n >")
        post_data["captcha"] = captcha_value
        # scrapy.FormRequest可以提供表单的提交
        # 这里的每一个FormRequest都要设置callback,因为scrapy是基于twisted框架的,是异步的
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=headers,  # 只要向知乎进行数据请求都要 指明headers
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




