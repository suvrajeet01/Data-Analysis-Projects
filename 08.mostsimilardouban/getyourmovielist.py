#! python3
from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
import pickle

def getmovie():
#cookies
    cookies = {}
    raw_cookies=input("Enter the cookies:")
    for line in raw_cookies.split(';'):
        key,value=line.split('=',1)#1代表只分一次，得到两个数据
        cookies[key[1:]]=value

    def find_next(soup):
        a = soup.find_all(class_="next")
        a = str(a)
        pattern = re.compile('<a href=\"(\S+)\"',re.S)
        next_url = re.findall(pattern,a)[0]
        return next_url

    def count_total(soup):
        a = soup.find_all('span')
        a = str(a)
        pattern2 = re.compile('data-total-page=\"(\S+)\"+',re.S)
        total_page = int(re.findall(pattern2,a)[0])
        return total_page

    def get_eachpage(soup):
        a = soup.find_all(class_="info")
        a = str(a)
        pattern = re.compile('https:\/\/movie.douban.com\/subject\/\d+',re.S)
        movies = re.findall(pattern,a)
        return movies


    url=input("请输入你的豆瓣电影集地址:")
    #url = "https://movie.douban.com/mine?status=collect"
    r= requests.get(url,cookies=cookies)
    soup = BeautifulSoup(r.content,"html.parser")
    number = count_total(soup)
    result = []
    for i in range(0,number,1):
        try:
            r= requests.get(url,cookies=cookies)
            soup = BeautifulSoup(r.content,"html.parser")
            result += get_eachpage(soup)
            url = find_next(soup)
            print("抓取下一页：" + url)
        except:
            break

    print("抓取完毕,一共有" + str(len(result))+ "记录")

    #写入list保存
    with open("mymovie.txt", "wb") as fp:
        pickle.dump(result, fp)

    return result

if __name__ == '__main__':
    result = getmovie()
#重新读取
#with open("mymovie.txt", "rb") as fp:
#   b = pickle.load(fp)
