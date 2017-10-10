#! python3
from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def get_location_id_name(page,dic):
        pattern = re.compile('浙江(\w+)交友_(.+)（佳缘ID:(\d+)）的个人资料_世纪佳缘交友网</title>',re.U | re.S)
        result = pattern.search(page)
        if result is not None:
            dic["nickname"] = result.group(2)
            dic["id"] = result.group(3)
            dic["location"] = result.group(1)
            return dic
    
def is_membership(page,dic):
    pattern = re.compile('<span class=\"member_dj\">(.*?)</span>', re.S)
    result = pattern.search(page)
    if result is not None:
        if "普通会员" in result.group(0):
            dic["membership"] = "普通会员"
        else:
            dic["membership"] = "高级会员"
    return dic

def get_brief_info(page,dic):
    pattern = re.compile('<h6 class=\"member_name\">(.*?)<', re.S)
    result = pattern.search(page)
    if result is not None:
        brief_info = result.group(1)
        dic["age"]= brief_info.split("，")[0]
        dic["marriaged"] =brief_info.split("，")[1]
    return dic

def get_basic_info(soup,dic): #基本信息
    try:
        list_info = soup.find_all('ul', {'class':"member_info_list"})[0].find_all('em')
        if len(list_info)>0:
            dic["education"] = list_info[0].text
            dic["height"] = list_info[1].text
            dic["car"] = list_info[2].text
            dic["salary"] = list_info[3].text
            dic["house"] = list_info[4].text
            dic["weight"] = list_info[5].text
            dic["constellation"] = list_info[6].text
            dic["ethnic"] = list_info[7].text
            dic["shengxiao"] = list_info[8].text
            dic["blood"] = list_info[9].text
            return dic
    except:
        return dic
        #return education,height,car,salary,house,weight,constellation,ethnic,shengxiao,blood
    #else:
     #   return None,None,None,None,None,None,None,None,None,None,
        
def js_info(soup,dic): #择偶要求,用soup
    try:
        js_list = soup.find_all('ul', {'class':"js_list"})[0].find_all('div')
        if len(js_list)>0:
            dic["js_age"] = js_list[0].text.replace(" ","")
            dic["js_height"] = js_list[1].text.replace(" ","")
            dic["js_ethnic"] = js_list[2].text.replace(" ","")
            dic["js_education"] = js_list[3].text.replace(" ","")
            dic["js_photo"] = js_list[4].text.replace("\xa0*","")
            dic["js_marriaged"] = js_list[5].text.replace(" ","")
            dic["js_location"] = js_list[6].text.replace(" ","").replace("\xa0*","")
            dic["js_member"] = js_list[7].text.replace(" ","")
            return dic
    except:
        return dic
    

file_name = input("输入id文档地址：")
input_name = file_name + ".csv"
output_name = file_name + "-info.csv"    
id_list = pd.read_csv(input_name)



final_list = []
cookies = {}
raw_cookies = input("enter the cookies：")

for line in raw_cookies.split(';'):
    key,value=line.split('=',1)#1代表只分一次，得到两个数据
    cookies[key[1:]]=value

count = 0
for i in id_list["id"][:]:
    count = count + 1
    dic ={}
    search_url = "http://www.jiayuan.com/"+ str(i)
    r= requests.get(search_url,cookies=cookies)
    soup = BeautifulSoup(r.content,"html.parser")
    try:
        dic = get_location_id_name(str(soup),dic)
        dic = is_membership(str(soup),dic)
        dic = get_brief_info(str(soup),dic)
        dic = get_basic_info(soup,dic)
        dic = js_info(soup,dic)
        if dic is not None:
            final_list.append(dic)
            df = pd.DataFrame(final_list)
            df.to_csv(output_name, encoding='utf-8')
        print("第"+ str(len(final_list))+ "用户的信息抓取完毕!" + "实际抓取的是第"+ str(count)+"个用户")
        if count % 1000 == 0:
            time.sleep(60)
    except:
        print("不是浙江的！")
        print(i)
        pass