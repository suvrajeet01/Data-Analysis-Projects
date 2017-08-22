#要用到的包
import numpy as np
import pandas as pd
import tkinter
from collections import defaultdict
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler

####################################################################################################
#主要协同过滤算法，需要安装有surprise包，重新跑一遍算法，也可以后续选择用已经跑出来的结果
#重新跑一边模型拟合，需要有surprise包
def do_algorithm():
    from surprise import SVD
    from surprise import Dataset
    from surprise import evaluate, print_perf
    from surprise import Reader, Dataset
    from surprise import SVD,KNNBasic
    import pickle
    # 定义格式
    reader = Reader(line_format='user item rating', sep=',')
    #加载数据集
    data = Dataset.load_from_file('data/rate.csv', reader=reader)
    data.split(n_folds=5) #数据集折叠，一般来说数值越大，误差越大

    #SVD算法
    def use_SVD():
        algo = SVD(n_factors=2) #调整
        return algo

    def use_knn():
        sim_options = {'name': 'cosine',
                   'user_based': False  # 计算相似性
                   }
        algo = KNNBasic(sim_options=sim_options)
        return algo

    algo = use_knn()
    algo_1 = use_SVD()
    #evaluate(algo, data, measures=['RMSE', 'MAE']) #检验'RMSE'

####################################################################################################
#基于资助关系算法所用到的函数#

    #功能函数
    result = pd.read_csv("data/result.csv")
    user = set(result["user"])
    item = set(result["item"])

    def get_item_id(name):
        location = result["item"].tolist().index(name)
        iid = result["itemid"].tolist()[location]
        return iid

    def get_item_name(iid):
        location = result["itemid"].tolist().index(int(iid))
        name = result["item"].tolist()[location]
        return name

    def get_user_name(uid):
        location = result["userid"].tolist().index(int(uid))
        name = result["user"].tolist()[location]
        return name

    def new_prediction(predictions): #假如用Knn就用这个新的prediction
        predictions_knn = []
        for i in predictions:
            if i.details['was_impossible'] == False:
                predictions_knn.append(i)
        return(predictions_knn)

    def get_top_n(predictions, n=10):
        # First map the predictions to each user.
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, est))
        # Then sort the predictions for each user and retrieve the k highest ones.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]
        return top_n

    #####################################################
    #使用基于资助关系和分数的KNN算法，拟合模型#
    trainset = data.build_full_trainset()
    algo.train(trainset)

    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)

    #用SVD
    trainset_1 = data.build_full_trainset()
    algo_1.train(trainset)
    testset_1 = trainset.build_anti_testset()
    predictions_1 = algo_1.test(testset)

    #使用knn算法
    use_knn =True
    if use_knn == True:
        predictions = new_prediction(predictions)
    top_n = get_top_n(predictions, n=5)

    top_n_1 = get_top_n(predictions_1, n=5)

    final_dict = {}
    final_dict_1 = {}

    # Print the recommended items for each user
    for uid, user_ratings in top_n.items():
        final_dict[get_user_name(uid)] = [get_item_name(iid) for (iid, _) in user_ratings] #得到最后的对应结果

    for uid, user_ratings in top_n_1.items():
        final_dict_1[get_user_name(uid)] = [get_item_name(iid) for (iid, _) in user_ratings] #得到最后的对应结果

    with open('data/knn_basic.pickle', 'wb') as handle:
        pickle.dump(final_dict, handle)

    with open('data/svn.pickle', 'wb') as handle:
        pickle.dump(final_dict_1, handle)

    return final_dict, final_dict_1

####################################################################################################
#使用已经拟合的模型所得出的推荐结果
def use_already_data():
    import pickle
    with open("data/knn_basic.pickle", "rb") as myFile:
        final_dict = pickle.load(myFile)
    with open("data/svn.pickle", "rb") as myFile:
        final_dict1 = pickle.load(myFile)
    return final_dict,final_dict1

####################################################################################################
#解释：对于没有信息的新基金会，根据基本信息找到现有260个基金会中最相似的一个
def find_nearest(input_list):
    data = pd.read_excel("data/索引.xlsx")
    name = data['基金会名字']
    final_selection = ['捐赠收入','总收入','境内捐赠','其他收入','自然人捐赠','公益事业支出','业务活动成本','总支出','全职员工'
                   ,'评估等级-未参评','行政办公支出','评估等级-5A','成立时间','管理费用','分数','心理健康','扶贫助困']
    final_data = data[final_selection]
    input_array = np.array([input_list])
    data_matrix = final_data.as_matrix()
    new_matrix = np.concatenate((data_matrix, input_array), axis=0) #添加到矩阵最后一列
    standardized_data = StandardScaler().fit_transform(new_matrix)

    dis_count = []
    new_input = standardized_data[-1]
    for i in standardized_data[:-1]:
        dis_count.append(euclidean_distances([i], [new_input])[0][0]) #计算和每项的距离值
    dis_count
    index_min = min(range(len(dis_count)), key=dis_count.__getitem__) #找到最小值
    return find_exist(data['基金会名字'][index_min])#返回的是基金会名字列表

####################################################################################################
#基于资助型基金会本身信息所用到的函数#

#解释：对于现有的基金会，根据基本信息找到现有260个基金会中最相似的一个
def find_nearest_old(user):
    data = pd.read_excel("data/索引.xlsx")
    location = data["基金会名字"].tolist().index(user)

    final_selection = ['捐赠收入','总收入','境内捐赠','其他收入','自然人捐赠','公益事业支出','业务活动成本','总支出','全职员工'
                   ,'评估等级-未参评','行政办公支出','评估等级-5A','成立时间','管理费用','分数','心理健康','扶贫助困']
    final_data = data[final_selection]
    data_matrix = final_data.as_matrix()
    standardized_data = StandardScaler().fit_transform(data_matrix)

    dis_count = []
    new_input = standardized_data[location]
    for i in standardized_data:
        if np.array_equal(i, new_input): #判断
            dis_count.append(100000000) #提高最大值
        else:
            dis_count.append(euclidean_distances([i], [new_input])[0][0]) #计算和每项的距离值
    index_min = min(range(len(dis_count)), key=dis_count.__getitem__) #找到除了本身之外的最小值
    return find_exist(data['基金会名字'][index_min]) #返回的是基金会名字列表

#从资助关系中找出每个资助型基金会分别投了什么受助型基金会
def find_exist(name):
    user_dict ={}
    result = pd.read_csv("data/result.csv")
    user = list(set(result["user"]))

    user_dict={}
    for i in user:
        a = result[result["user"] == i]["item"]
        user_dict[i] = [name for name in a]
    return user_dict[name]

import re
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#转换日期函数
from datetime import date
def input_date(text):
    a = text.split("-")
    d0 = date(int(a[0]),int(a[1]),int(a[2]))
    d1 = date(1900, 1, 1)
    delta = d0 - d1
    return (delta.days)

##########################################################################################################
#输入17个通过PCA方法选取出来的特征，获得numpy的array,用于计算距离
def input_new():
    text_list =[]
    final_selection = ['捐赠收入(元)','总收入(元)','境内捐赠(元)','其他收入(元)','自然人捐赠(元)','公益事业支出(元)','业务活动成本(元)','总支出(元)','全职员工'
                   ,'评估等级是否为“未参评”(是请输1，否请输0)',
                       '行政办公支出(元)','基金会评估等级是否为“5A”(是请输1，否请输0)','成立时间(YYYY-MM-DD)','管理费用(元)',
                       '透明度分数','行业领域是否包括“心理健康”(是请输1，否请输0)',
                       '行业领域是否包括“扶贫助困”(是请输1，否请输0)']
    for i in final_selection:
        text = input(i+":")
        if i == '成立时间(YYYY-MM-DD)':
            right_date = True
            while(right_date == True):
                try:
                    text = input_date(text) #转换时间差
                    right_date = False
                except:
                    text = input("请输入正确格式的日期：")
        while(is_number(text) == False):
            print("不是数字，请重输入")
            text = input(i+":")
        text = float(text)
        text_list.append(text)
    print("\n")
    return text_list
##########################################################################################################
def input_name(name):
    text = "" #基于相互关系(knn)
    text2 = "" #基于基本信息
    text3= ""  #新的基金会
    text4="" #基于相互关系(svd)

    if name in final_dict:
        for i in final_dict[name]:
            text = text + "\n" + i

    data_basicinfo = pd.read_excel("data/索引.xlsx")
    if name in data_basicinfo["基金会名字"].tolist():
        for i in find_nearest_old(name):
            text2 = text2 + "\n" + i

    if name in final_dict1:
        for i in final_dict1[name]:
            text4 = text4 + "\n" + i

    if len(text4) > 6: #是否有SVD
        if len(text)>6: #是否有KNN
            if len(text2)>6: #是否有相互关系
                return("*基于资助关系推荐(KNN)*" + text + "\n"+"\n*基于资助关系推荐(SVD)*" + text4 + "\n"+ "\n*基于资助型基金会基本信息推荐*" + text2)
            else:
                return("*基于资助关系推荐(KNN)*" + text + "\n"+"\n*基于资助关系推荐(SVD)*" + text4)
        else:
            if len(text2)>6: #是否有相互关系
                return("*基于资助关系推荐(SVD)*" + text4 + "\n"+"\n*基于资助型基金会基本信息推荐*" + text2)
            else:
                return("*基于资助关系推荐(SVD)*" + text4 + "\n")
    else:
        print("该基金会不在数据库中/或者不是资助型基金会，请输入相关信息方便我们为你匹配对应的受助型基金会！")
        input_list = input_new()
        for i in find_nearest(input_list):
            text3 = text3 + "\n" + i
            return("*基于资助型基金会基本信息推荐*" + text3)
##########################################################################################################
num = input("请选择:\n1.我已经安装好surprise包，重新跑一次模型\n2.利用已经存在本地数据库\n(请输入数字):")
#print("\n")
num_tag = True
while(num_tag == True):
    if num == "1":
        final_dict,final_dict1 = do_algorithm()
        num_tag = False
    elif num =="2":
        final_dict,final_dict1 = use_already_data()
        num_tag = False
    else:
        num = input("请输入正确数字！")

Quit_tag = True
while(Quit_tag == True):
    name = input("请输入资助型基金会名称：")
    print("\n")
    print(input_name(name))
    print("\n")
    choice = input("是否查询其他基金会？y/n:")
    if choice in ["Y","y","是"]:
        pass
    else:
        print("\n结束！")
        Quit_tag = False
