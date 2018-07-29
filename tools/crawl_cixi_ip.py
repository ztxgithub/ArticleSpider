# -*- coding: utf-8 -*-

import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host='127.0.0.1', user='root', password='123456',
                                                database='article_spider', charset="utf8",
                                                use_unicode=True)
cursor = conn.cursor()

"""
    爬取西刺免费代理 IP
"""

def crawl_ips():
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)" \
                 " AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/63.0.3239.108 Safari/537.36"

    headers = {
        "User-Agent": user_agent
    }

    for i in range(1500):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers = headers)
        selector = Selector(text=re.text)
        """
            在 id 为 ip_list 的节点下的 tr 节点
            <table id="ip_list">
              <tr class="odd">
                <td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png" alt="Cn"></td>
                <td>122.237.104.62</td>
                <td>80</td>
                <td>浙江绍兴</td>
                <td class="country">高匿</td>
                <td>HTTPS</td>
                  <td>2小时</td>
                <td>7分钟前</td>
              </tr>
        """
        all_trs = selector.css("#ip_list tr")
        ip_list = []
        """
            tr 也是一个 selector 选择器
        """
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            speed = 0
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_texts = tr.css("td::text").extract()
            ip = all_texts[0]
            port = all_texts[1]
            protocol = all_texts[5]
            ip_list.append((ip, port, speed, protocol))

        for ip_info in ip_list:
            insert_sql = """
                            insert into proxy_ip(ip, port, speed, proxy_type)
                            values(%s, %s, %s, %s);
                         """

            cursor.execute(insert_sql, (ip_info[0], ip_info[1],
                                        ip_info[2], ip_info[3]))
            # cursor.execute(
            #     "insert into proxy_ip(ip, port, speed, proxy_type) values('{0}', '{1}', {2}, {3})".format(
            #         ip_info[0], ip_info[1], ip_info[2], ip_info[3]
            #     )
            # )

            conn.commit()

"""
    从数据库中获取ip
"""
class GetIP(object):
    """
        将 ip:port 从数据库中进行删除
    """
    def delete_ip_db(self, ip, port):
        delete_sql = """
            delete from proxy_ip where ip = '{0}' and port = '{1}'
        """

        cursor.execute(delete_sql.format(ip, port))
        conn.commit()
        return True
    """
        判断 ip 是否可用
    """
    def judge_ip(self, ip, port):
        http_url = "http://www.baidu.com"
        proxy_url = "https://{0}:{1}".format(ip, port)

        """
            进行 try 操作，如果请求正常则证明该 proxy_url 可用
        """
        try:
            """
                对应 requests 模块可以传递 proxy(http)
            """
            proxy_dict = {
                "http": proxy_url
            }
            """
                向百度请求数据，不过不是通过自身的 ip 而是通过代理(proxy)
            """
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("requests error invalid proxy ip:port")
            # 从数据库中删除该 ip:port
            self.delete_ip_db(ip, port)
            return False

        ret_code = response.status_code
        if ret_code >= 200 and ret_code < 300:
            print("valid ip")
            return True
        else:
            print("invalid ip and port")
            # 从数据库中删除该 ip:port
            self.delete_ip_db(ip, port)
            return False

    def get_random_ip(self):
        random_sql = "select ip, port from proxy_ip order by RAND() LIMIT 1"
        cursor.execute(random_sql)

        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            re_judeg = self.judge_ip(ip, port)

            if re_judeg:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


if __name__ == "__main__":
    get_ip = GetIP()
    get_ip.get_random_ip()