#爬取了每个基金会的财务信息
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import re
import pandas as pd
from itertools import permutations

def year_select(lis):
    if ("2013年","2014年","2015年") in (z for z in permutations(lis,3)):
        year_data = [lis[0],lis[1],lis[2],lis[3]]
    else:
        if ("2013年","2014年") in (z for z in permutations(lis,2)):
            year_data = [lis[0],lis[1],lis[2],None]
        elif ("2014年","2015年") in (z for z in permutations(lis,2)):
            year_data = [lis[0],None,lis[1],lis[2]]
        elif ("2013年","2015年") in (z for z in permutations(lis,2)):
            year_data = [lis[0],lis[1],None,lis[2]]
        elif ("2013年") in lis:
            year_data = [lis[0],lis[1],None,None]
        elif ("2014年") in lis:
            year_data = [lis[0],None,lis[1],None]
        elif ("2015年") in lis:
            year_data = [lis[0],None,None,lis[1]]
        else:
            year_data = [lis[0],None,None,None]
            print("请检查这个网站数据"+lis[0])
    return year_data

def get_asset(url,df,driver):
    driver.get(url)
    time.sleep(3)
    #driver.find_element_by_link_text(year).click()
    html=driver.page_source
    soup=BeautifulSoup(html,'lxml')
    content = soup.findAll('tspan')
    lis = [item.text for item in content]
    #driver.close()
    if len(lis)>0:
        index = len(df) + 1
        year_data = year_select(lis)
        #print(year_data)
        df.set_value(index, "name", year_data[0])
        df.set_value(index, "2013", year_data[1])
        df.set_value(index, "2014", year_data[2])
        df.set_value(index, "2015", year_data[3])
        df.set_value(index, "url", url)
    return df

df = pd.read_csv("url.csv")
new_df= pd.DataFrame(data=None, index=None, columns=["name","2013","2014","2015","url"])

driver = webdriver.Chrome()
for url in df["url"][4112:]:
    final = get_asset(url,new_df,driver)
    final.to_csv('asset_detail.csv', encoding='utf-8')
