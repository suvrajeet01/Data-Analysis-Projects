from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd

#爬取个人电影页面
dataframe = pd.DataFrame.from_csv("sample.csv")

cookies = {}
raw_cookies = input("enter the cookies：")
#raw_cookies='ll="108289"; bid=4a89RwhDSCc; __utmt=1; __utma=30149280.2125343414.1497989209.1497989209.1498000258.2; __utmb=30149280.2.10.1498000258; __utmc=30149280; __utmz=30149280.1497989209.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.2125343414.1497989209; _gid=GA1.2.230149405.1498000349; _gat_UA-7019765-1=1; ue="clarkyu1993@outlook.com"; dbcl2="162795734:uwDhinrc7Ag"'

for line in raw_cookies.split(';'):
    key,value=line.split('=',1)#1代表只分一次，得到两个数据
    cookies[key[1:]]=value

dataframe["已经看过的电影"] = ''
dataframe["想看的电影"] = ''
dataframe["注册日期"] = ''

def find_movie(soup):
    a = soup.find_all("h2")
    text =""
    for item in a:
        text = text + str(item)
    pattern1 = re.compile('target.+>(\d+\S+)看过',re.S)
    pattern2 = re.compile('target.+>(\d+\S+)想看',re.S)
    num_movies1 = re.findall(pattern1,text)
    num_movies2 = re.findall(pattern2,text)
    return num_movies1,num_movies2

def register(soup):
    date_str = str(soup.find_all('div', class_="pl"))
    pattern = re.compile('<br.+(.{9}\d)加入',re.S)
    pattern1 = re.compile('<br/>.+(.........\d)加入',re.S)
    try:
        date = re.findall(pattern,date_str)[0]
    except:
        date = re.findall(pattern1,date_str)[0]
    return date

for i in range(len(dataframe)):
    url = dataframe["个人主页"][i]
    print("开始读取" + str(url))
    r= requests.get(url,cookies=cookies)
    soup = BeautifulSoup(r.content,"html.parser")
    num_movies1,num_movies2 = find_movie(soup) #观影数量
    date = register(soup) #注册时间

    dataframe.set_value(i, "已经看过的电影", num_movies1)
    dataframe.set_value(i, "想看的电影", num_movies2)
    dataframe.set_value(i, "注册日期",  date)

    print("结束，下一个")
    time.sleep(3)
    dataframe.to_csv('addwatch.csv', encoding='utf-8')
