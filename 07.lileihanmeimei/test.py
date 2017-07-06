#! python3
from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd

def to_string(item):
    paragraphs = []
    for x in item:
        paragraphs.append(str(x))
    return paragraphs[3]

def get_info(item):
    pattern = re.compile('<a class.+?>(\S+)<',re.S)
    name = re.findall(pattern,item)
    pattern3 = re.compile('<a class=.+href=\"(.+)/\">',re.S)
    url = re.findall(pattern3,item)

    try:
        pattern2 = re.compile('<span class=.+?title=\"(.+)\"></span>',re.S)
        rate = re.findall(pattern2,item)
        return (name[0],rate[0], url[0])
    except:
        return (name[0],None, url[0])

def find_next(soup):
    next = str(soup.find_all('a', class_="next")[0])
    print(next)
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
    return "https://movie.douban.com/subject/26289138/comments"+new.replace('amp&','')

cookies = {}
raw_cookies=input("Enter the cookies:")
#raw_cookies='ll="108289"; bid=4a89RwhDSCc; _ga=GA1.2.2125343414.1497989209; _gid=GA1.2.230149405.1498000349; ck=Ahu4; __utma=223695111.2125343414.1497989209.1498001315.1498001315.1; __utmb=223695111.0.10.1498001315; __utmc=223695111; __utmz=223695111.1498001315.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __utma=30149280.2125343414.1497989209.1497989209.1498000258.2; __utmb=30149280.6.10.1498000258; __utmc=30149280; __utmz=30149280.1497989209.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=30149280.16279; ue="clarkyu1993@outlook.com"; dbcl2="162795734:Fd+B1qoPnjc"'
for line in raw_cookies.split(';'):
    key,value=line.split('=',1)#1代表只分一次，得到两个数据
    cookies[key[1:]]=value

url = "https://movie.douban.com/subject/26289138/comments"
result = set()
for i in range(0,5800,1):
    print('正在爬取'+ url)
    r= requests.get(url,cookies=cookies)
    soup = BeautifulSoup(r.content,"html.parser")
    print("导入为soup")
    a = soup.find_all('h3')
    print("升级url")
    url = find_next(soup)
    print("准备写入！")
    for item in a:
        print(get_info(to_string(item)))
        result.add(get_info(to_string(item)))
    print("结果写入完成！" + "目前有数据条数：" + str(len(result)))
    print("睡眠开始！")
    time.sleep(3)
    print("睡眠结束！再次爬行！")
    current_result = pd.DataFrame(list(result),columns=['用户姓名','评分情况','个人主页'])
    current_result.to_csv('result_current.csv', encoding='utf-8')

final_result = pd.DataFrame(list(result),columns=['用户姓名','评分情况','个人主页'])
final_result.to_csv('result.csv', encoding='utf-8')
