from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

df= pd.DataFrame(data=None, index=None, columns=["url","age"])

def geturl(soup,df,age):
    data = soup.findAll('a',attrs={'class':'os_stat'})
    for i in data:
        try:
            df.loc[-1] = [i["href"],age]  # adding a row
            df.index = df.index + 1  # shifting index
        except:
            print ("出错了！")
            pass
    return df

#登陆世纪佳缘
login_url ='http://www.jiayuan.com/'
driver = webdriver.Chrome()
driver.get(login_url)
account = driver.find_element_by_xpath('//*[@id="hder_login_form_new"]/input[3]')
account.send_keys('13586720652')
password =driver.find_element_by_xpath('//*[@id="hder_login_form_new"]/input[4]')
password.send_keys('1993717')
account.send_keys(Keys.RETURN)
time.sleep(5)

go = True
age = 18 #起始18岁

def loop_age(df):
    print("开始爬取"+str(age) + "年龄段的用户")
    page = 1
    count_same = 0
    go = True
    count_old = 0
    while(go == True):
        search_url = "http://search.jiayuan.com/v2/index.php?key=&sex=m&stc=1:3308,2:18.0,23:1&sn=default\
        &sv=1&pt=41&ft=off&f=select&mt=d&p=%d" %page                               
        driver.get(search_url)
        time.sleep(2)
        html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(html,'lxml')
        final = geturl(soup,df,age).drop_duplicates().reset_index()
        final.to_csv('衢州.csv', encoding='utf-8')
        print("翻到了第"+ str(page) + "页")
        print("已经抓取了"+ str(len(final))+ "位用户的信息")
        count_new = len(final)
        print(count_old)
        print(count_new)
        if count_new != count_old:
            count_old = count_new
            page += 1
        else:
            count_same +=1
            if count_same == 3:
                go = False
            else:
                page += 1
loop_age(df)