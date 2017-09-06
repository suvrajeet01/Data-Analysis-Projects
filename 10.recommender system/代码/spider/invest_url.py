from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import re
import pandas as pd

def get_url(soup,df):
	asset = soup.findAll('td', {"width":"70","align":"right"})
	pattern1 = re.compile('<a href=\"/(.+)\" target',re.S)
	for i in range(0,len(asset)):
	    try:
	        url = re.findall(pattern1,str(asset[i]))[0]
	    except:
	        url = None
	    index = len(df) + 1
	    df.set_value(index, "url", "http://data.foundationcenter.org.cn/"+url)
	return df
	    

#添加地址

df= pd.DataFrame(data=None, index=None, columns=["url"])
driver = webdriver.Chrome()
driver.get("http://data.foundationcenter.org.cn/foundation.html")
time.sleep(5)

for i in range(1,250,1):
    html=driver.page_source
    soup=BeautifulSoup(html,'lxml')
    df = get_url(soup,df)
    df.to_csv('url.csv', encoding='utf-8')
    try:
        driver.find_element_by_id("next1").click()
    except:
        time.sleep(20)
        driver.find_element_by_id("next1").click()
    time.sleep(6)
    print("结束第！" + str(i))

