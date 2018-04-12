#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import pandas as pd
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.cluster import KMeans
#from mpl_toolkits.mplot3d import Axes3D
import calculate_distance #用于计算两个坐标距离
import get_location
from sklearn.cluster import DBSCAN


path = "home/hotel/bigdata/data/"

##预处理##
df= pd.read_csv(path + "gps_location.csv") #下载包含经纬度的数据，主要有clientID,openuuid,经纬度和上传时间构成
df.columns = ['clientId','openuuid', 'latitude',"longitude","uploadtime"] #重构字段名
test_client = list(df['clientId'].unique())

def extract_date(t): #将日期字符串转换为日期的时间格式
    return t.date()  
def convert_time(i):#从日期字段中提取小时
    t = i.time()
    new_hour = t.hour + t.minute / 60.0 + t.second /3600.0
    return new_hour

upload_time = pd.to_datetime(df['uploadtime'])
df['uploadtime'] = upload_time.apply(convert_time)
df["date"] = upload_time.apply(extract_date)

def get_center_by_kmeans(df):
    dataset = df.as_matrix(['longitude','latitude','iswork']) #对经纬度和工作状态三个字段进行聚类k-means用
    min_max_scaler = preprocessing.MinMaxScaler() #标准化
    dataset_minmax = min_max_scaler.fit_transform(dataset)
    clf = KMeans(n_clusters=1,random_state=42) #选取两个聚类
    s = clf.fit(dataset_minmax)
    labels = clf.labels_ 
    center = clf.cluster_centers_  #返还两个聚类的中心点
    return min_max_scaler.inverse_transform(center)[0]

def use_DBSCAN(current_df,user_n,i):
    #print "数据点比较多使用DBSCAN算法！"
    dataset = current_df.as_matrix(['longitude','latitude'])
    kms_per_radian = 6371.0088 #地球平均半径
    epsilon = 0.5 / kms_per_radian #距离为0.5千米进行聚类
    y_pred = DBSCAN(eps = epsilon, min_samples = 2,algorithm='ball_tree', metric='haversine').fit_predict(np.radians(dataset)) #球形距离计算
    current_df["label"] = y_pred

    #获取最大的两个label标签 注意新版本sort已经变成sort_values
    #.index.values
    if current_df.label.nunique()> 1: #判断DBSCAN是否生成两个聚类：
        #print current_df.label.nunique()
        top_values = current_df.groupby(["label"]).count().sort(["iswork"],ascending=False)[:2].index.values #获取列表
        df_0 = current_df[current_df["label"] ==top_values[0]]
        df_1 = current_df[current_df["label"] ==top_values[1]]

        center_1 = get_center_by_kmeans(df_0)
        center_2 = get_center_by_kmeans(df_1)
        df_center = pd.DataFrame([center_1, center_2],columns=['longitude','latitude','iswork'])    

    else: #DBSCAN算法无法区分聚类，因为数据值过小
        center_only = get_center_by_kmeans(current_df)
        df_center = pd.DataFrame([center_only,center_only],columns=['longitude','latitude','iswork']) #为了不改动合成函数，此字段不变   
    return df_center

def use_kmeans(df,user_n,i):
    #print "数据点比较少使用kmeans算法！"
    dataset = df.as_matrix(['longitude','latitude','iswork']) #对经纬度和工作状态三个字段进行聚类k-means用
    min_max_scaler = preprocessing.MinMaxScaler() #标准化
    dataset_minmax = min_max_scaler.fit_transform(dataset)
    clf = KMeans(n_clusters=2,random_state=42) #选取两个聚类
    s = clf.fit(dataset_minmax)
    labels = clf.labels_ 
    center = clf.cluster_centers_  #返还两个聚类的中心点
    df['label'] = labels
    df_center = pd.DataFrame(min_max_scaler.inverse_transform(center), columns=['longitude','latitude','iswork'])
    return df_center

##清洗数据##
def cleaning_outliers(df): #df为每单独clientID用户的dataframe
    
    def home_or_not(row): #对工作和非工作时间段进行判定
        if row["uploadtime"] >= 9 and row["uploadtime"] <= 18:   #假设9点-18点为工作时间
            row["iswork"] = 1
        elif row["uploadtime"] >= 7 and row["uploadtime"] <9:
            row["iswork"] =0.5
        elif row["uploadtime"] > 18 and row["uploadtime"] <=19:
            row["iswork"] =0.5
        else:
            row["iswork"] = 0
        return row
    df=df.apply(home_or_not,axis=1)
    
    def cal_dist(row,lat,lng): #在表中创建新字段“距离”，用于计算每行中的经纬度与某一特定地点的地理距离，单位为千米
        return calculate_distance.calcDistance_two(row["latitude"],row["longitude"],lat,lng)
    
    
    #率先排除上传异常值，将每天的上传次数进行统计，去除当日上传次数大于选取时间段平均每日上传次数的日期
    data_df2 = df.groupby(["date"]).count()
    keep_date2 = list(data_df2[data_df2.uploadtime - data_df2.uploadtime.mean()< 3* data_df2.uploadtime.std()].index.values)
    df = df[df['date'].isin(keep_date2)]
    
    #对同一天中的坐标异常值的点进行处理，去除离当天平均坐标距离超过一个标准差的点
    outliers = []
    for day in df["date"].unique(): 
        new_df = df.groupby(['date']).get_group(day)
        avg_lat = new_df.latitude.mean()
        avg_lng = new_df.longitude.mean()
        new_df["distance"] = new_df.apply(cal_dist,lat =avg_lat,lng=avg_lng,axis=1)
        outlier = list(new_df[np.abs(new_df.distance-new_df.distance.mean())>(2*new_df.distance.std())].index.values)
        outliers = outliers + outlier   
    df.drop(outliers, inplace=True)
    
    #将每天的平均坐标进行比较，去除当日平均坐标与选取时间段内平均坐标距离超过一个标准差的日期（用于排除节假日特殊情况）
    data_df = df.groupby(["date"]).mean()
    avg_lat = data_df.latitude.mean()
    avg_lng = data_df.longitude.mean()
    data_df["distance"] = data_df.apply(cal_dist,lat =avg_lat,lng=avg_lng,axis=1)
    keep_date = list(data_df[np.abs(data_df.distance-data_df.distance.mean())<=(2*data_df.distance.std())].index.values)#setting ceil and floor for large distance
    df = df[df['date'].isin(keep_date)]
    return df

##进行聚类##
def draw_user(df,user_n,i):
    #print "进行算法聚类！"
#     dataset = df.as_matrix(['longitude','latitude','iswork']) #对经纬度和工作状态三个字段进行聚类k-means用
#     min_max_scaler = preprocessing.MinMaxScaler() #标准化
#     dataset_minmax = min_max_scaler.fit_transform(dataset)
    
#     dataset2 = df.as_matrix(['longitude','latitude']) #DBSCAN
    #if len(df) >= 10:
    result = use_DBSCAN(df,user_n,i)
    #else:
        #result = use_kmeans(df,user_n,i)
    return result

##main运算
n = 0
center_df = pd.DataFrame(None, columns=['clientId','longitude','latitude','iswork'])
for i in test_client: #遍历用户的clientID
    current_df = df[df["clientId"] == i] #生成每个用户的数据表
    old_num = len(current_df)
    if len(current_df)<=2: #如果用户数据小于或等于两行，无法进行聚类
        #print "数据点太少" + "用户" + str(i) + "无法进行聚类！"
        pass
    else:
        try:
            current_df = cleaning_outliers(current_df)
            #print "user"+ str(i) + " keep " + str(float(len(current_df))/float(old_num)) + " location points"
            test_df = draw_user(current_df,n,i)#绘图
            test_df["clientId"] = i #添加用户clientID
            center_df = center_df.append(test_df)
            n = n + 1
        except:
            n = n + 1
        pass


final_result = get_location.get_location(center_df)
final_result.to_csv(path + "location_info.csv",encoding="utf_8_sig") #将数据保存为csv格式