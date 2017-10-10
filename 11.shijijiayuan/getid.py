from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

df= pd.DataFrame(data=None, index=None, columns=["url"])
def geturl(soup,df):
    data = soup.findAll('a',attrs={'class':'os_stat'});
    for i in data:
        index = len(df)
        try:
            df.set_value(index, "url", i["href"])
        except:
            print (i)
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
page = 1
current_num = 0
while(go== True):
    search_url = "http://search.jiayuan.com/v2/index.php?key=&sex=f&stc=1:3310,2:31.0,23:1&sn=default&sv=1&pt=50&ft=off&f=select&mt=d&p=" + str(page)
    driver.get(search_url)
    time.sleep(2)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup=BeautifulSoup(html,'lxml')
    final = geturl(soup,df).drop_duplicates().reindex()
    final.to_csv('taizhou31+.csv', encoding='utf-8')
    print("翻到了第"+ str(page) + "页")
    print("已经抓取了"+ str(len(final))+ "位用户的信息")
    page += 1