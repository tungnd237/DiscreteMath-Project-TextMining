import os
import config
import text_mining as tm
import pandas as pd
import os
import webscraping


#data = config.DATA_DIR
stopwords = config.STOPWORDS
#os.chdir(data)

# iterate through all file
#list_title = []

#for file in os.listdir():
    # Check whether file is in text format or not
    #if file.endswith(".txt"):
        #file_path = f"{data}\{file}"

        # call read text file function
        #list_title.append(tm.read_text_file(file_path).strip()[:50])

#df = pd.DataFrame(list_title, columns=['title'])
#basePath = os.path.dirname(os.path.abspath(__file__))
#df = pd.read_json(basePath + '\webscraping\data\vnexpress.json', lines = True, orient = "records",encoding = 'utf8'
                  #, dtype={"'category'":str, "url":str, "title": str, "text": str})

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

### Run graph
output,position=tm.remove_similar(df_title,stopword_vn,plot_original=True,plot_result=True)
