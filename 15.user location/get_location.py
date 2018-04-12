#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import pandas as pd
import numpy as np
import calculate_distance
import requests


def get_location(df):
    #把main.py中得到的数据进行整合
    left_df = df[df.index == 1].reset_index()
    right_df = df[df.index==0].reset_index()
    result = pd.concat([left_df, right_df], axis=1)

    result=result.loc[:,[False,True,True,True,True,False,False,True,True,True]]
    result.columns = ["clientId","is_work1","lat1","lng1","is_work2","lat2","lng2"]

    result["distance_diff"] = 0 #建立距离列，计算两个中心点的距离
    def add_more(row):
        row["distance_diff"] = calculate_distance.calcDistance_two(row["lat1"],row["lng1"],row["lat2"],row["lng2"])
        return row
    result = result.apply(add_more,axis = 1)

    def covert_float(i):
        return float(i)
    result["is_work1"] = result["is_work1"].apply(covert_float)
    result["is_work2"] = result["is_work2"].apply(covert_float)

    final_df = result
    #final_df = result[(result["distance_diff"]<30) & (result["distance_diff"]>0)] #根据两个中心点距离进行筛选，排除不切实际的预测
    pic_list = list(final_df.index) #将保留的图片标号储存为列表

    ##统一格式，左边为家庭住址，右边为办公住址
    def exchange_row(row):
        a = row["lng1"]
        b = row["lat1"] 
        c = row["is_work1"] 
        if row["is_work2"] < row["is_work1"]:
            row["lng1"], row["lat1"],row["is_work1"] = row["lng2"], row["lat2"],row["is_work2"]
            row["lng2"], row["lat2"],row["is_work2"] = a,b,c
        return row

    final_df = final_df.apply(exchange_row,axis = 1)

    final_df["clear"],final_df["city"],final_df["home_address"],final_df["home_road"],final_df["work_address"],final_df["work_road"] = 0,0,0,0,0,0

    ##根据经纬度返还百度地图实际地址##
    def get_location(lng,lat):
        base = 'http://api.map.baidu.com/geocoder/v2/?ak=FnL3GE3mocMaGdAUIheP5pFm&output=json'
        location = '&location=' + str(lat) + ',' + str(lng)
        url = base + location
        answer = requests.get(url).json()
        location = answer["result"]["formatted_address"]
        info = answer["result"]["sematic_description"]
        city = answer["result"]["addressComponent"]["city"]
        return city,location,info
    
    def get_location_gd(lng,lat):
        base = 'http://restapi.amap.com/v3/geocode/regeo?output=json&key=6fbc8ac2d6fdff5e5943b92919d6b8d2'  #单日2000条
        location = '&location=' + str(lng) + ',' + str(lat)
        url = base + location
        answer = requests.get(url).json()
        location = answer["regeocode"]["formatted_address"]
        road = answer["regeocode"]["addressComponent"]["streetNumber"]["street"]+ answer["regeocode"]["addressComponent"]["streetNumber"]["number"]
        if len(answer["regeocode"]["addressComponent"]["city"]) <1:
            city = answer["regeocode"]["addressComponent"]["province"]
        else:
            city = answer["regeocode"]["addressComponent"]["city"]
        return city,location,road

    def add_location_info(row):
        row["city"],row["home_address"],row["home_road"] = get_location_gd(row["lng1"],row["lat1"])
        row["city"],row["work_address"],row["work_road"] = get_location_gd(row["lng2"],row["lat2"])
        if row["distance_diff"] <= 0.5:
            row["clear"] = "F"
        else:
            row["clear"] = "T"
        return row

    final_df = final_df.apply(add_location_info,axis = 1)
    
    return final_df
    #final_df.to_csv("location_info_test.csv",encoding="utf_8_sig") #将数据保存为csv格式