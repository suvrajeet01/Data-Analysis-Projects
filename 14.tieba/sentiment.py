import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
yue1 = pd.read_excel("1yue.xlsx")
from aip import AipNlp
APP_ID = '10909247'
API_KEY = 'yEhHvGw126yPXcQmzAGYR7Ls'
SECRET_KEY = 'MQliVxQdGxtUZU5oCyqUxBTEE1oP1KOR'
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
def content_df(df):
    positive = 0
    negative = 0
    num = 0
    for content in df["content"]:
        try:
            sentiment = client.sentimentClassify(str(content))
            positive += sentiment['items'][0]['negative_prob']
            negative += sentiment['items'][0]['positive_prob']
            num += 1
            print(positive,negative,num)
        except:
            pass    
    return(positive,negative,num)
result = content_df(yue1)
print(result)