#爬取2015年投资信息
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import re
import pandas as pd


def add_detail(soup,df):
    ids = soup.findAll('td', {"align":"center","width":"40"})[1:] #id
    users = soup.findAll('td', {"style":"width:150px","tbl":"org"}) #user
    items = soup.findAll('a', {"style":"padding-left:3px;"}) #item
    moneys = soup.findAll('td', {"style":"text-align:center;","width":"90"}) #money
    years = soup.findAll('td', {"align":"right","width":"75"}) #year

    for i in range(0,len(ids)):
        try:
            id = ids[i].text
        except:
            id = None

        try:
            user= users[i]["title"]
        except:
            user= None

        try:
            item = items[i]["title"]
        except:
            item = None

        try:
            money = moneys[i].text.replace(" ","").replace("\n","")
        except:
            money = None

        try:
            year = years[i].text.replace(" ","").replace("\n","")
        except:
            year = None

        index = len(df) + 1
        df.set_value(index, "id", id)
        df.set_value(index, "user", user)
        df.set_value(index, "item", item)
        df.set_value(index, "money", money)
        df.set_value(index,"year",year)

    return df

print("开始！")
df= pd.DataFrame(data=None, index=None, columns=["id","user","item","money","year"])
driver = webdriver.Chrome()
driver.get("http://data.foundationcenter.org.cn/donation.html")
time.sleep(15)

for i in range(1,653,1):
    html=driver.page_source
    soup=BeautifulSoup(html,'lxml')

    df = add_detail(soup,df)
    df.to_csv('touzi.csv', encoding='utf-8')

    driver.find_element_by_id("next1").click()
    time.sleep(5)

    #测试是否加载出来
    html_test=driver.page_source
    soup_test=BeautifulSoup(html_test,'lxml')
    test = soup_test.findAll('td', {"align":"center","width":"40"})[1:]
    while len(test) < 20:
        print("加载不出来啦！")
        time.sleep(10)
        html_test=driver.page_source
        soup_test=BeautifulSoup(html_test,'lxml')
        test = soup_test.findAll('td', {"align":"center","width":"40"})[1:]

    print("结束第！" + str(i))
