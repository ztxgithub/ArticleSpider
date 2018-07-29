# -*- coding: utf-8 -*-
from selenium import webdriver
from scrapy.selector import Selector

"""
    生成一个 webdriver
    executable_path 对应于下载的 chromedriver.exe 的绝对路径
"""

browser = webdriver.Chrome(executable_path="D:/exe_path/chromedriver.exe")

browser.get("https://detail.tmall.com/item.htm?id=567202730288&ali_refid=a3_430583_1006:1122559733:N:%E7%94%B7%20%E9%9E%8B%20%E7%94%B7:1ebc971368542c48ae452bdea1acd91f&ali_trackid=1_1ebc971368542c48ae452bdea1acd91f&spm=a230r.1.14.1")

"""
    这个 browser.page_source 实际上是通过浏览器运行完
    js 后的生成的 html 页面
"""
print(browser.page_source)

# 新开的浏览器关闭
browser.quit()


# 天猫价格获取
browser.get("https://detail.tmall.com/item.htm?spm=a230r.1.14.3.yYBVG6&id=538286972599&cm_id=140105335569ed55e27b&abbucket=15&sku_properties=10004:709990523;5919063:6536025")
t_selector = Selector(text=browser.page_source)
print(t_selector.css(".tm-promo-price .tm-price::text").extract())
# print(browser.page_source)
browser.quit()

"""
    知乎模拟登陆
    1.模拟浏览器找到 "登录" 按钮点击
    2.找到输入用户名的元素 进行输入 (send_keys)
    3.找到输入密码的元素 进行输入 (send_keys)
    4.找到 "登录" 按钮进行 点击(click)
"""
browser.get("https://www.zhihu.com/signup?next=%2F")
browser.find_element_by_css_selector(".SignContainer-switch span").click()
browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input[name='username']").send_keys("18092671458")
browser.find_element_by_css_selector(".SignFlow-password .SignFlowInput .Input-wrapper input[name='password']").send_keys("ty158917")
browser.find_element_by_css_selector(".Button.SignFlow-submitButton.Button--primary.Button--blue").click()

# selenium 完成微博模拟登录
browser.get("http://weibo.com/")
"""
   这里要进行 sleep 是因为网页中 js 代码还没完全加载完，就开始 find_element_by_css_selector
   这样有些元素是找不到的
"""
import time
time.sleep(5)
browser.find_element_by_css_selector("#loginname").send_keys("1147727180@qq.com")
browser.find_element_by_css_selector(".info_list.password input[node-type='password'] ").send_keys("ty409760")
browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()

"""
    执行 javascript 代码完成鼠标下拉功能
    
"""
# 开源中国博客:selenium执行JavaScript
browser.get("https://www.oschina.net/blog")
import time
time.sleep(5)
for i in range(3):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
    time.sleep(3)

# 设置chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(executable_path="./chromedriver.exe",chrome_options=chrome_opt)
browser.get("https://www.oschina.net/blog")

# phantomjs, 无界面的浏览器， 多进程情况下phantomjs性能会下降很严重

browser = webdriver.PhantomJS(
    executable_path="C:/spiderDriver/phantomjs-2.1.1-windows/bin/phantomjs.exe")
browser.get("https://detail.tmall.com/item.htm?spm=a230r.1.14.3.yYBVG6&id=538286972599&cm_id=140105335569ed55e27b&abbucket=15&sku_properties=10004:709990523;5919063:6536025")
t_selector = Selector(text=browser.page_source)
print (t_selector.css(".tm-price::text").extract())
# print (browser.page_source)
browser.quit()

if __name__ == "__main__":
    print(browser.page_source)