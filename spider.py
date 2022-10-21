#-*- codeing = utf-8 -*-
#@Time : 2022/10/14 22:17
#@Author : lnn
#@File : spider.py
#@Software: PyCharm
# print("hello")  #只有同种数据类型才能相加print("hello"+str(a)) 或者print("hello",a)

import bs4    #帮助我们进行网页解析、获取数据   （爬完网页，把里面的数据进行拆分）
import re     #正则表达式，进行文字匹配的       （进行数据的提炼）
import urllib.request,urllib.error     #指定url，获取网页数据      （对网页，进行爬）
import xlwt       #进行excel操作           （存在excel中）
import sqlite3     #进行SQLite数据库操作   （存到数据库）


def main():
    #1.爬取网页
    baseurl="https://movie.douban.com/top250?start="

    datalist=getData(baseurl)
    # savepath="豆瓣电影Top250.xls"
    dbpath="movie.db"
    # 3.保存数据
    # saveData(datalist,savepath)
    saveData2DB(datalist,dbpath)
#影片详情链接的规则   (.*)一组若干个字   （.*？）一组链接
findLink=re.compile(r'<a href="(.*?)">')     # 创建正则表达式对象，表示规则（字符串的模式）
#影片图片
findImgSrc=re.compile(r'<img.*src="(.*?)"',re.S)    #re.S让换行符包含在字符中
#影片片名
findTitle=re.compile(r'<span class="title">(.*)</span>')
#影片评分
findRating=re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
findJudge=re.compile(r'<span>(\d*)人评价</span>')
#找到概况
findInq=re.compile(r'<span class="inq">(.*)</span>')
#找到影片的相关内容
findBd=re.compile(r'<p class="">(.*?)</p>',re.S)   #忽视换行符
#爬取网页
def getData(baseurl):
    datalist=[]
    for i in range(0,10):   #调用获取页面信息的函数，10次
        url=baseurl +str(i*25)
        html=askURL(url)    #保存获取到的网页源码
        # 2.逐一解析数据，每获取一个网页解析一次
        soup= bs4.BeautifulSoup(html,"html.parser")
        # 查找符合要求的字符串形成列表        class加下划线是为了和python内部的class区分开
        for item in soup.find_all("div",class_="item"):
            # print(item)   #测试查看电影item全部信息
            data=[]   #保存一部电影的所有信息
            item=str(item)    #把item变成字符串形式，就可以使用正则表达式进行解析啦
            #link获取影片的详情链接      re.findall默认返回的是一个列表，列表【0】就是返回列表的第一个
            link=re.findall(findLink,item)[0]   #re库用来通过正则表达式查找指定的字符串
            data.append(link)           #添加链接

            imgSrc=re.findall(findImgSrc,item)[0]
            data.append(imgSrc)         #添加图片

            titles=re.findall(findTitle,item)       #片面可能只有一个中文，也可能有中英两个
            if(len(titles)==2):
                ctitle=titles[0]
                data.append(ctitle)             #添加中文名
                otitle=titles[1].replace("/","")    #把外文名替换去掉前面的斜杠，无关符合去掉
                data.append(otitle)             #添加外国名
            else:
                data.append(titles[0])
                data.append(' ')                #外国名没有的时候要留好空。因为后面是要存excel\数据库中，别乱行

            rating=re.findall(findRating,item)[0]
            data.append(rating)                    #添加评分

            judgeNum=re.findall(findJudge,item)[0]
            data.append(judgeNum)                   #添加评价人数

            inq=re.findall(findInq,item)
            if(len(inq)!=0):
                inq=inq[0].replace("。","")          #去掉句号
                data.append(inq)                        #添加概述
            else:
                data.append(" ")                #若没有概述，为其留空

            bd=re.findall(findBd,item)[0]
            bd=re.sub('<br(\s+)?/>(\s+)?'," ",bd)     #去掉br
            bd=re.sub('/'," ",bd)                   #替换/
            data.append(bd.strip())                 #把bd去掉前后空格后添加进去
            datalist.append(data)       #把处理好的一部电影的信息放入datalist
    # print(datalist)
    return datalist


#得到指定一个URL的网页内容
def askURL(url):
    head={      #模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
#用户代理表示告诉豆瓣服务器，我们是什么类型的机器、浏览器（本质上是告诉浏览器我们可以接收什么水平的文件内容）
    request=urllib.request.Request(url,headers=head)
    html=""
    try:
        response=urllib.request.urlopen(request)
        html=response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):       #判断e对象里面是否包含code属性
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html
#3.保存数据到excel中
def saveData(datalist,savepath):
    book=xlwt.Workbook(encoding="utf-8",style_compression=0)    #创建excel文件
    sheet=book.add_sheet("豆瓣电影Top250",cell_overwrite_ok=True)      #创建sheet1表单
    col=("电影详情链接","图片链接","影片中文名","影片外国名","评分","评价数","概况","相关信息")     #对列进行定义。用的是小括号元组
    for i in range(0,8):
        sheet.write(0,i,col[i])         #列名
    for i in range(0,250):
        print("第%d条"%(i+1))
        data=datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])      #数据添加
    book.save(savepath)

#4.保存数据到数据库sqlite中
def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn=sqlite3.connect(dbpath)
    cur=conn.cursor()       #拿到cursor，下面就该执行语句了
    #我们为每一条电影信息生成一条sql语句，然后执行一次
    for data in datalist:
        for index in range(len(data)):
            if index==4 or index==5:
                continue
            data[index]='"'+data[index]+'"'
        sql='''
                insert into movie250(
                info_link, pic_link, cname, ename, score, rated, introduction, info) 
                values (%s)'''%",".join(data)    #s表示   把data列表中的每一个内容用逗号相分隔
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()



#5.初始化数据库（下面一整个过程就是建表。先创建、再连接创建的文件、再使用cursor、再cursor执行语句、再提交、最后关闭）
def init_db(dbpath):
    # 创建数据表
    sql='''
        create table movie250(
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar ,
        ename varchar ,
        score numeric ,
        rated numeric ,
        introduction text,
        info text
        )
    
    '''
    conn=sqlite3.connect(dbpath)        #连接（创建）文件
    cursor=conn.cursor()                #游标cursor
    cursor.execute(sql)                 #cursor执行sql语句（建表）
    conn.commit()                       #提交执行的语句
    conn.close()                        #关闭

#当程序执行时,作为整个程序的入口，控制多个函数之间的关系和流程，更清楚的管理代码的主流程
if __name__ == '__main__':
    #调用函数
    # init_db("movietest.db")
    main()
    print("爬取完毕！")