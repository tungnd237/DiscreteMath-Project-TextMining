import os
import config
import text_mining as tm
import pandas as pd


data = config.DATA_DIR
stopwords = config.STOPWORDS
os.chdir(data)

# iterate through all file
list_title = []

for file in os.listdir():
    # Check whether file is in text format or not
    if file.endswith(".txt"):
        file_path = f"{path}\{file}"

        # call read text file function
        list_title.append(tm.read_text_file(file_path).strip()[:50])

df = pd.DataFrame(list_title, columns=['title'])

### stopword vietnam
f = open(stopwords, 'r',encoding="utf8")
stopword_vn = f.read().split('\n')

### Run graph
df_sample = df.sample(50, replace = True)
df_sample = df_sample.reset_index(drop=True)
output,position=tm.remove_similar(df_sample,stopword_vn,plot_original=True,plot_result=True)
