# -*- coding: utf-8 -*-

#首先说结论：selenium真的不如requests+splash_api好用！

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
import requests
from PyPDF2 import PdfReader, PdfMerger
import os
import time

#合并mooc文件夹中所有pdf文件，同时添加目录
#文件夹在同级不必使用'./xx/',直接用'xx/',文件夹在上级必须用'../xx/'
def merge(folder='mooc/'):
    #从文件夹读取的文件排序有问题，必须解决10.0在1.0后面的问题，问题在于标题是字符串比较大小
    #sorted(list,key=排序方案，reverse=)是系统内置的排序函数，list.sort(key=,reverse)是列表的属性
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
def write(source,url):
    tree=html.fromstring(source)
    name=tree.xpath('/html/body/div[4]/div[2]/div[4]/div[2]/div/div[1]/div/div/div[1]/div[1]/div/div[2]/div/div[1]/text()')[0]
    href=tree.xpath('//*[@id="courseLearn-inner-box"]/div/div/div[3]/div[4]/a/@href')
    #xpath获得即使只有一个也是列表形式，必须用href[0]获取字符串
    #mooc网对referer进行检测，不正确就打不开下载链接
    content=requests.get(href[0],headers={'referer':url}).content
    with open('mooc/'+name+'.pdf','wb') as f:
        f.write(content)
        
#driver.find_element 获得第一个  driver.find_elements 获得所有的列表  classname的空格必须用.代替
#selenium获得元素索引一刷新页面就失效了，用一个必须从新获取一次
#mooc网加载出详细页再返回，无关章节会自动折叠，我们必须重新打开所有章节
def open_detail():
    elements=driver.find_elements(By.CLASS_NAME,'f-icon.cpicon.j-up.f-fl.u-icon-caret-down')  #'titleBox.j-titleBox.f-cb')
    for element in elements:
        #textContent获取文本 innerHTML 获取子元素 outerHTML获取当前选定元素及其子元素
        outer=element.get_attribute('outerHTML') 
        if  'display: none;' not in outer:
            element.click()

#设置无头模式,应该和close()一起用，不然好像没法关闭网页，总之不太影响美观且很麻烦
# option=webdriver.ChromeOptions()
# option.add_argument('--headless')
# 需在webdriver.Chrome()中添加options!!!

#获取chromedriver的安装路径，如果没有就自动安装合适版本
driver_path=ChromeDriverManager().install()
#driver_path = 'C:/Users\86152\.wdm\drivers\chromedriver\win32/111.0.5563\chromedriver.exe'
#路径建议养成使用斜杠'/'的习惯，避免可能的转义或转码
driver = webdriver.Chrome(executable_path=driver_path)
#置空webdriver属性，防止网站屏蔽selenium
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', 
                       { 'source':' Object.defineProperty ( navigator,"webdriver", {get:()=>undefined} )' } )
#强制等待 import time   time.sleep(3)  如果是等待网页渲染，只能用这种等待
#隐式等待 有时间  先查找某一元素，找到就过，没找到就等待t秒，再尝试一次，依然没有就返回异常
driver.implicitly_wait(3) 
#之所以不适用于网页渲染，因为一开始肯定能找到源码，就不会等待，但不是渲染完全的源码
#显式等待 有时间和条件 先判断条件是否成立,成立则按时间规则等待,条件不成立或者超时就抛出异常
# WebDriverWait(driver,5,0.5).until( EC.presence_of_element_located( (By.ID),'su' ) )
#最长等待5秒，每0.5秒查询一次,until是等待条件

url='https://www.icourse163.org/learn/CSU-1002475002?tid=1468200512#/learn/content'
driver.get(url)
#添加cookies或token或session实现登录，有些网站不登录提取不到信息
#暂停一下，进行登录。(不能采样无头模式) 有些用法可以参照‘自动登录选课网站.py’
# input('请在网页上登录账号，完成以后回到这里按任意键继续。')
# print(driver.get_cookies())
#此处第一遍直接手动登录，获取cookies,复制给下面的变量,之后一段时间就不用再登录了
driver.delete_all_cookies() 
cookies= [{'domain': '.icourse163.org', 'httpOnly': False, 'name': 'NETEASE_WDA_UID', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1140412498#|#1526045773547'}, {'domain': '.icourse163.org', 'expiry': 1681916838, 'httpOnly': True, 'name': 'STUDY_PERSIST', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '"R1cFpTSC+rnqu6kAYVDQSe/bh1qmu+yEA4XYj/Isy0LlnwRCkREdSkh5ouNqcKAY9EgMdSmdzomgVhGH6xTtKZytLG0AFuGv3mPEw3b7L4OpwHrhDEHCjUW1qNyobk6LFmFsXe4q0ae/onsOWOFtcufbC2nER1NzYGoeUvhNtSYRgJD0jlQnwct9FtDDiKpLWsO3I2dwYD8mhebYaJlMdQOVYOKjB7qDEc3jOp5/Kn/ZgpjCC7Iso4RP9U87vJE8LtaQzUT1ovP2MqtW5+L3Hw+PvH8+tZRDonbf7gEH7JU="'}, {'domain': '.icourse163.org', 'httpOnly': True, 'name': 'STUDY_SESS', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '"LGx90hNCX/7eULfzIBYmNFH9/IEB1enZsqGzuwEoAFD8OE5DU0SfMShyeZrB/dL5Uz6UDehISfEqBxoCwwsYZlr07FJlM1UBM6wfnNS+lo8PLgrlzaDq0sSsOxaM/tghm6Ugs2lNzCHTpaYFrpx6kJ4VZp9lTVwnq3A9T2a3dvALhur2Nm2wEb9HcEikV+3FTI8+lZKyHhiycNQo+g+/oA=="'}, {'domain': '.icourse163.org', 'httpOnly': True, 'name': 'NTES_YD_SESS', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'xKl7yo_4fHNiWcZK_ZgxqZpHX44f3YultXZbI.SuI2qENK67NXivTdwdcC76CmWeqTPJYLxSOTrFMzpOtabWJcYNWmUozMyr0BQaQbtkJji3sK4UoLjIuJv4gxNSxh5VToExxWSSAeuidxbYXFwlHgg.cbB9XnbeWqmk7KQMwRKDZaCBjjvxq9aqbaeW4cXE4Ul9.QuwDJSuKjjajiese.UDOCmkFphF2LvPR21RpHSfH'}, {'domain': '.icourse163.org', 'expiry': 1710860842, 'httpOnly': False, 'name': 'Hm_lvt_77dc9a9d49448cf5e629e5bebaa5500b', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1679324823'}, {'domain': 'www.icourse163.org', 'expiry': 1713884823, 'httpOnly': False, 'name': 'WM_NIKE', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '9ca17ae2e6ffcda170e2e6eeaaf36681edfab2f0218d928bb6c54a938e9badd86fa7abf9d2e53fa7f19996db2af0fea7c3b92a81ecaeabf67ab8b4f7a5c469b38bbc95d23dad90b793b23b81b6aea6f052fb8a9892e17cf49abf89bc7c8d99a5d6c76faabeb884d34692aaffd3bc63bcb5fe8dd54f8a90a0a8cc5ff7aabf83b873aebda98bdc49bb90bcbac2499cebbe8dc64094a78ed2cf63fbe9a1b4fc53acadc094f25ef288a4d3d161bc9bb9d5e87bfc9d9ba7c837e2a3'}, {'domain': '.icourse163.org', 'httpOnly': False, 'name': 'STUDY_INFO', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '"yd.1298da7edf774d389@163.com|8|1140412498|1679324837862"'}, {'domain': '.icourse163.org', 'expiry': 1680145638, 'httpOnly': True, 'name': 'NTES_YD_PASSPORT', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'Ar4dgvvJLZ.6z3R2BIQ3ZqE9I_vTiDKhg47GIbgtLJq768YH69PjrGIGKEHYEb3p5rORcgwZzrhMMYV6n0Hu3SXMMsqZlDllp1fn_hy5.JNCvOZt2ZhQNcJGH55lZMib4UeGE.Pv4nunYlIkw3MEv0vdA48XqnnyRH6aWNvyN70voF5J03jjHHXnvluOjxPcGSoCOQJ5lMniB25zQh9SWHdfC'}, {'domain': 'www.icourse163.org', 'expiry': 1713884823, 'httpOnly': False, 'name': 'WM_TID', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'N2dW%2FOWMBulBRQQQBAaEbO%2Br0KpK%2FT%2FS'}, {'domain': 'www.icourse163.org', 'expiry': 1710860823, 'httpOnly': False, 'name': '__yadk_uid', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '2qFhJUVTZS3N0wK152OXcii3EWvcgqji'}, {'domain': '.icourse163.org', 'expiry': 1713884820, 'httpOnly': False, 'name': 'EDUWEBDEVICE', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'b4e7de5a8dc0411cb7b31f4e0dd61a00'}, {'domain': 'www.icourse163.org', 'expiry': 1713884823, 'httpOnly': False, 'name': 'WM_NI', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'C4bJwrtl9DAcqUttS7oPyr31CjbEmZ9VXqbp0Fqh9pOGk5DejbxcPNRv129ixk2lVEJPPGIU5vqb5yncgjYCyPtYCCX5rlG4PyB1Li97oSyYhspssV2Xl2RkxEw4eq8CUFE%3D'}, {'domain': '.icourse163.org', 'httpOnly': False, 'name': 'Hm_lpvt_77dc9a9d49448cf5e629e5bebaa5500b', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1679324842'}, {'domain': '.icourse163.org', 'httpOnly': False, 'name': 'NTESSTUDYSI', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '2f0b4dc84bd045d088c6571218cc84a6'}, {'domain': 'www.icourse163.org', 'httpOnly': False, 'name': 'CLIENT_IP', 'path': '/learn', 'sameSite': 'Lax', 'secure': False, 'value': '101.94.164.241'}]
for cookie in cookies:
    driver.add_cookie(cookie)
#登录之后重新访问一下
# driver.refresh()
driver.get(url)
#打开所有章节,不打开是找不到所需要的内容,因为mooc采样js生成html,不点击就没有元素
open_detail()
#selenium获取的元素只在刷新前有效,只能先获取总数,然后一个一个来
num=len(driver.find_elements(By.XPATH,'//*[contains(@title,"（PPT）")]'))
for i in range(num):
    element=driver.find_elements(By.XPATH,'//*[contains(@title,"（PPT）")]')[i]
    element.click()
    time.sleep(1) #等待网页渲染
    write(driver.page_source,driver.current_url) #请求下载pdf
    driver.back() #退回章节页
    open_detail() #重新获取元素索引
driver.close() #driver.quit()

merge() #合并保存的pdf


