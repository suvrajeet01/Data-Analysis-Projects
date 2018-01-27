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
    

def run_task(start_num,store_name):

    #file_name = input("输入id文档地址：")
    input_name = "sxlist.csv"
    output_name = store_name +  "到"+ str(start_num+600) + ".csv"    
    id_list = pd.read_csv(input_name)
    final_list = []
    cookies = {}
    #raw_cookies = input("enter the cookies：")
    raw_cookies = "photo_scyd_168337151=yes; SESSION_HASH=9dc750be27ef6cd33d1114c247cd1ef7122ec941; user_access=1; REG_REF_URL=; save_jy_login_name=13586720652; sl_jumper=%26cou%3D17%26omsg%3D0%26dia%3D0%26lst%3D2017-10-21; last_login_time=1508568483; upt=EA5QRwC4Mqu5SuTwLeL1M2559QkAStmD%2ATKpwAUp78fha8ns1R4Txv8Ck2rNJoccqDdTIuwUdwhE7TJ8aIg.; user_attr=000000; stadate1=167337151; myloc=33%7C3301; myage=24; PROFILE=168337151%3A%25E4%25BD%25B3%25E7%25BC%2598%25E5%25BE%2581%25E5%25A9%259A%3Am%3Aimages1.jyimg.com%2Fw4%2Fglobal%2Fi%3A0%3A%3A1%3Azwzp_m.jpg%3A2%3A1%3A50%3A10; mysex=m; myuid=167337151; myincome=10; RAW_HASH=BzqdIrGHRjhN27LL5BHz2fR3TGOEJQ5chOuwvZr-nORMszypsEOAT3j6Y-Dd4-KHity3lIcD2-khUPy%2AWD8DR0-VK0pE3yPEAqwBL%2AX%2AAnmx0MQ.; COMMON_HASH=83e9417e38e2d65c04d54e7700bbf6b2"
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    for line in raw_cookies.split(';'):
        key,value=line.split('=',1)#1代表只分一次，得到两个数据
        cookies[key[1:]]=value

    count = 0
    
    if start_num == 3000:
        end_num = 3200
    else:
        end_num = start_num + 600
    for i in id_list["id"][start_num:end_num]:
        status = False
        count = count + 1
        dic ={}
        search_url = "http://www.jiayuan.com/"+ str(i)

        while(status == False):
            r= requests.get(search_url,cookies=cookies,headers=headers)
            if r.status_code != 200:
                print("被禁止了！")
                time.sleep(60)
            else:
                status = True

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
            print("抓取的是"+ str(start_num) + "到" + str(start_num+600) + "的用户")
            print("第"+ str(len(final_list)+start_num)+ "用户的信息抓取完毕!" + "实际抓取的是第"+ str(count+start_num)+"个用户")
        except:
            print("不是浙江的！")
            print(i)
            pass