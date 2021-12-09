from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
import random as rd
import config
import text_mining as tm
import pandas as pd
import numpy as np
import webscraping

stopwords = config.STOPWORDS
#use unsupervised learning to remove similar content

#as dbscan is not fit for the mission
#we use the simplest algorithm as a bench player
#although the result of kmeans is bounded by linearity
#the result of kmeans is quite intuitive and time-efficient

#estimate parameters of linear equation
def get_line_params(x1,y1,x2,y2):

    a=(y1-y2)/(x1-x2)
    b=y1-a*x1

    return a,b

#compute perpendicular distance
def get_distance(x,y,a,b):

    temp1=y-x*a-b
    temp2=(a**2+1)**0.5

    return np.abs(temp1/temp2)

def kmeans_algo(df,stopword,maxk=50,**kwargs):

    #convert text to feature vectors
    df['clean']=[' '.join(
        tm.preprocessing(i,stopword,lower=True)) for i in df['title']]
    train=CountVectorizer()
    train_matrix=train.fit_transform(df['clean'])

    #viz and get k
    optimal=get_optimal_k(train_matrix,maxk=maxk,**kwargs)

    #kmeans
    clf= KMeans(optimal)
    clf.fit(train_matrix)

    return clf.labels_

#elbow method for kmeans to find the optimal k
def get_optimal_k(train_matrix,maxk=50,plot_elbow=False):

    #compute inertia
    sse=[]
    for i in range(1,maxk):
        clf=KMeans(n_clusters=i)
        clf.fit(train_matrix)
        sse.append(clf.inertia_/10000)

    #elbow method for kmeans
    a,b=get_line_params(0,sse[0],len(sse)-1,sse[-1])

    distance=[]
    for i in range(len(sse)):
        distance.append(get_distance(i,sse[i],a,b))

    #get optimal k
    optimal=distance.index(max(distance))

    return optimal

def recommendation2(df,stopword,**kwargs):

    #the worst case of a clustering problem is n//2 clusters
    #where n is the number of data points
    #hence, we set maxk to len(df)//2+1
    df['class']=kmeans_algo(df,stopword,maxk=len(df)//2+1,**kwargs)

    #within each label, its the same story written by different reporters
    #so we randomly select one as our final output
    result=[]
    for i in set(df['class']):
        cluster=df[df['class']==i].index.tolist()
        result.append(rd.choice(cluster))

    data=df.loc[result]
    data.reset_index(inplace=True,drop=True)
    del data['clean']

    return data,result

webscraping.crawl_data()

df_vnexpress = pd.read_csv(r'webscraping/data/vnexpress.csv', encoding = "utf8")
df_laodong = pd.read_csv(r'webscraping/data/laodong.csv', encoding = "utf8")

list_df = []

for i in df_vnexpress['category'].unique():
    if i != 'category':
        list_df.append(df_vnexpress[['title', 'url']][df_vnexpress.category == i].iloc[:15].copy())

list_df.append(df_laodong[df_laodong.title != 'title'][['title', 'url']])#.sample(50))

df_title = pd.concat(list_df, axis = 0)
df_title = df_title.dropna()
df_title = df_title.reset_index(drop = True)
df_title = df_title[df_title.title != "title"]

### stopword vietnam
f = open(stopwords, 'r',encoding="utf8")
stopword_vn = f.read().split('\n')

### time to run graph theory
start = datetime.now()
tm.recommendation(df_title,stopword_vn)
print("graph theory running time:", datetime.now() - start)

### time to run KNN
start = datetime.now()
recommendation2(df_title,stopword_vn)
print("KNN running time:", datetime.now() - start)
