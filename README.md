# 利用python+selenium自动下载慕课网上课程的所有ppt
最近在慕课上学习的时候，想把每小节的ppt下载下来放在平板里，这样方便一边看视频一边在ppt上勾画，但是整个课程有将近30个PPT，自己去一个点开再下载很麻烦，就想用刚学的selenium做一个自动化脚本，于是便有这个项目。
### 依赖环境
1. 安装python解释器
2. 安装chrome浏览器
3. 安装相关依赖包:   
#### pip install selenium,webdriver-manager,lxml,requests,PyPDF2

### 三个主要步骤：
- 利用selenium点开网页,提取下载链接
- 利用requests下载PTT并保存到本地
- 利用pypdf2合并所有PPT并添加目录
---
*我也是边学边做,想着把知识实践一下,做个小项目有点成就感.  如果有什么问题,欢迎您的建议!*
