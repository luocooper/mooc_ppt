# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
import requests
from PyPDF2 import PdfReader, PdfMerger
import os
import time


#合并mooc文件夹中所有pdf文件，同时添加目录
def merge(folder='mooc/'):
    #从文件夹读取的文件排序有问题，必须解决10.0在1.0后面的问题，问题在于标题是字符串比较大小
    #sorted(list,key=排序方案，reverse=)是系统内置的排序函数
    listdir=sorted(os.listdir(folder),key=lambda x :float(x.split()[0]) ) 
    merger = PdfMerger()
    page=0
    for item in listdir:
        merger.append(folder+item)       # 合并 pdf
        merger.add_outline_item(item, page)  # 添加目录项并指向合并的pdf的头页
        pages = PdfReader(folder+item).pages  # .pages获得读进来的pdf的页数
        page += len(pages)     
    merger.write('matlab.pdf') #保存合并的文件
    merger.close()

#两个参数分别是ppt页面的源码和链接，找到下载链接，然后请求内容并保存为pdf
def write_ppt(source,url):
    tree=html.fromstring(source)
    name=tree.xpath('/html/body/div[4]/div[2]/div[4]/div[2]/div/div[1]/div/div/div[1]/div[1]/div/div[2]/div/div[1]/text()')[0]
    href=tree.xpath('//*[@id="courseLearn-inner-box"]/div/div/div[3]/div[4]/a/@href')
    #xpath获得即使只有一个也是列表形式，必须用href[0]获取字符串
    #mooc网对referer进行检测，不正确就打不开下载链接
    content=requests.get(href[0],headers={'referer':url}).content
    with open('mooc/'+name+'.pdf','wb') as f:
        f.write(content)
        
#driver.find_element 获得第一个  driver.find_elements 获得所有的列表  classname的空格必须用.代替
#selenium获得元素索引在刷新页面后就失效了，用一次必须从新获取一次
#mooc网加载出详细页再返回，无关章节会自动折叠，我们必须重新打开所有章节
def open_detail():
    elements=driver.find_elements(By.CLASS_NAME,'f-icon.cpicon.j-up.f-fl.u-icon-caret-down')  #'titleBox.j-titleBox.f-cb')
    for element in elements:
        #outerHTML获取当前选定元素及其子元素
        outer=element.get_attribute('outerHTML') 
        if  'display: none;' not in outer:
            element.click()

#设置无头模式,应该和close()一起用，不然好像没法关闭网页，总之不太影响美观且很麻烦
# option=webdriver.ChromeOptions()
# option.add_argument('--headless')
# 需在webdriver.Chrome()中添加options!!!

#获取chromedriver的安装路径，如果没有就自动安装合适版本
driver_path=ChromeDriverManager().install()
driver = webdriver.Chrome(executable_path=driver_path)
#置空webdriver属性，防止网站屏蔽selenium
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', 
                       { 'source':' Object.defineProperty ( navigator,"webdriver", {get:()=>undefined} )' } )
#隐式等待  先查找某一元素，找到就过，没找到就等待t秒，再尝试一次，依然没有就返回异常
driver.implicitly_wait(3) #设置一次,对整个driver周期都有效
url='https://www.icourse163.org/learn/CSU-1002475002?tid=1468200512#/learn/content' #慕课上的某课程
driver.get(url)
#添加cookies或token或session实现登录，有些网站不登录提取不到信息
#暂停一下，进行登录。(不能采样无头模式) 
input('请在网页上登录账号，完成以后回到这里按enter继续。')
print(driver.get_cookies())
#此处第一遍直接手动登录，获取cookies,复制给下面的变量,之后一段时间就不用再登录了(注释上面两行,给下面四行解注)
#driver.delete_all_cookies() 
#cookies=  #将print(driver.get_cookies())的内容复制到此处
#for cookie in cookies:
#   driver.add_cookie(cookie)
#登录之后重新访问一下
driver.get(url)
#打开所有章节,不打开就找不到所需要的内容,因为mooc采样js生成html,不点击就没有元素
open_detail()
#selenium获取的元素只在刷新前有效,只能先获取总数,然后一个一个来
num=len(driver.find_elements(By.XPATH,'//*[contains(@title,"（PPT）")]'))
for i in range(num):
    element=driver.find_elements(By.XPATH,'//*[contains(@title,"（PPT）")]')[i]
    element.click()
    time.sleep(1) #等待网页渲染
    write_ppt(driver.page_source,driver.current_url) #请求下载pdf
    driver.back() #退回章节页
    open_detail() #重新获取元素索引
driver.close() 

merge() #合并保存的pdf
