#! python3
from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
import pickle

with open("mymovie.txt", "rb") as fp:
    movie_list = pickle.load(fp)

def to_string(item):
    paragraphs = []
    for x in item:
        paragraphs.append(str(x))
    return paragraphs[3]

def get_url(item):
    pattern3 = re.compile('<a class=.+href=\"(.+)/\">',re.S)
    url = re.findall(pattern3,item)
    return url

def find_next(soup,initial_url):
    next = str(soup.find_all('a', class_="next")[0])
    pattern = re.compile('<a class="next\".+href=\"(\S+)\">',re.S)
    url = re.findall(pattern,next)[0]
    url.split(";")
    new = ""
    count = 0
    for i in url.split(";"):
        if count == 0:
            new = i
        else:
            new = new + "&" + i
        count = count + 1
    return initial_url+ new.replace('amp&','')

cookies = {}
raw_cookies=input("Enter the cookies:")
for line in raw_cookies.split(';'):
    key,value=line.split('=',1)#1代表只分一次，得到两个数据
    cookies[key[1:]]=value

user_url = set()
count = 1
for movie in movie_list:
    url = movie + "/comments"
    initial_url = url
    print("开始爬取第" + str(count) + "部电影的评分用户地址: " + url)
    for i in range(0,300000,1):
        try:
            r= requests.get(url,cookies=cookies)
            soup = BeautifulSoup(r.content,"html.parser")
            #print("导入为soup")
            a = soup.find_all('h3')
            url = find_next(soup,initial_url)
            for item in a:
                text = (to_string(item))
                user_url.add(get_url(text)[0])
            print("结果写入完成！" + "目前有数据条数：" + str(len(user_url)))
            time.sleep(3)
            print("睡眠结束！再次爬行！")
            df = pd.DataFrame(list(user_url), columns=["User"])
            df.to_csv('user_list.csv', index=False)
        except:
            break
    count += 1
    time.sleep(20)
