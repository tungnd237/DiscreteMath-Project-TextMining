import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import nltk
import csv

def read_text_file(file_path):
    with open(file_path, "r") as f:
        return f.read()#.encode('latin1').decode('utf16')

### function for preprocessing step.
# Since we use Vietnamese articles, the lemmatization and steamming step can be skipped.
def preprocessing(text,stopword,lower=True,is_lemma=False,is_stemma=False):

    text_clean=text if lower==False else text.lower()

    #tokenize, remove stop words
    token=[]

    for i in nltk.tokenize.RegexpTokenizer(r'\w+').tokenize(text_clean):
        if i not in stopword:
            token.append(i)

    #lemmatization
    if is_lemma:
        text_processed=[]
        for i in token:
            text_processed.append(nltk.stem.wordnet.WordNetLemmatizer().lemmatize(i))
    else:
        text_processed=token

    #stemming
    if is_stemma:
        output=[]
        for i in text_processed:
            output.append(nltk.stem.PorterStemmer().stem(i))
    else:
        output=text_processed

    #remove numbers since they are also stopword
    remove_list =[]
    for i in output:
        remove_list.append(i)

    for i in remove_list:
        try:
            float(i)
            output.remove(i)
        except:
            pass

    return_list = []
    for i in output:
        if i not in stopword:
            return_list.append(i)

    return return_list

#find common words between two titles
#return the number of common words as the weight of the edge
def find_common_words(title_1,title_2,stopword):

    common=set(title_1).intersection(set(title_2)).difference(set(stopword))

    return len(common)

#add word list as an additional column.
def add_word_column(df,stopword,**kwargs):

    word_column=[]

    for i in df['title']:
        word_column.append(preprocessing(i,stopword,lower=True,**kwargs))
    df['word'] = word_column

    return df

#building undirected weighted graph using networkx
#we cannot use the original title as the node name
#it is simply too long for a node name
#thus, we have to use dataframe index as the node name
#we only connect two nodes if they share common words (exclude stopword)
#we set the number of common words as the weight of the edge
labeldict = {}

def build_graph(df, stopword):
    graph = nx.Graph()

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            w = find_common_words(df['word'][i], df['word'][j], stopword)
            if w != 0:
                labeldict[i] = df['title'][i]
                labeldict[j] = df['title'][j]
                graph.add_edge(i, j, weight=w)

    # print title and postition
    return graph

# plotting the graph structure
def graph_visualization(graph, position, nodecolor=[], nodesize=[],
               nodecmap=plt.cm.copper, title=None, colorbartitle=None,
               plot_colorbar=False, **kwargs):
    if not nodecolor:
        nodecolor = [0] * len(graph)
    if not nodesize:
        nodesize = 200

    ax = plt.figure(figsize=(20, 10)).add_subplot(111)

    nx.draw(graph, node_size=nodesize, pos=position,
            node_color=nodecolor, cmap=nodecmap, with_labels=True, **kwargs)

    # remove axes
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # plot colorbar for node color
    if plot_colorbar:
        sm = plt.cm.ScalarMappable(cmap=nodecmap,
                                   norm=plt.Normalize(vmin=min(nodecolor),
                                                      vmax=max(nodecolor)))
        sm._A = []
        cb = plt.colorbar(sm, ticks=[min(nodecolor), max(nodecolor)])
        cb.ax.set_yticklabels(cb.ax.get_yticklabels(), fontsize=11)
        cb.ax.set_ylabel(colorbartitle, fontsize=11, rotation=270)

    plt.xticks([])
    plt.yticks([])
    plt.title(title, fontsize=15)
    plt.savefig("apps/static/assets/img/output.jpg")
    plt.show()

#for some titles, they may not share any common words with others
#in another word, they are not included in the graph structure
#we gotta add them back to the output list, cant leave the minority behind
#even though they are not key information published by every website
#they could still be some exclusive or niche information that has value to us
def add_non_connected(df,output,graph):

    for i in range(len(df)):
        if i not in list(graph.nodes):
            output.append(i)

    return output

#graph traversal
def graph_traversal(graph):

    #dictionary of all vertices and weightes in graph
    dict_vertex =dict(graph.degree)

    #order dict by each node's weight
    dict_vertex =dict(sorted(dict_vertex.items(),key=lambda x:x[1],reverse=False))

    queue=list(dict_vertex.keys())
    recommendeded_vertices=[]

    #define a queue find the node with the highest agree.
    #The iteration will run until the queue is empty.
    while queue:

        V=queue.pop()
        recommendeded_vertices.append(V)

        redundant=set(queue).intersection(set(graph.neighbors(V)))

        for i in redundant:
            queue.remove(i)

    return recommendeded_vertices

#use graph theory to pick highlighted content
def recommendation(df, stopword, plot_original=False,
                   plot_result=False,**kwargs):
    # tokenization
    df = add_word_column(df, stopword, **kwargs)

    # graph building
    graph = build_graph(df, stopword, **kwargs)

    # fix node position for visual comparison
    pos = nx.spring_layout(graph, k=0.3)

    # plot original
    if plot_original:
        graph_visualization(graph, position=pos,
                   title='Original', **kwargs)

    # traversal to get the recommended vertices/ articles
    recommended_articles = graph_traversal(graph)

    # plot result, highlight the result
    if plot_result:
        nodecolor = []
        for i in graph.nodes:
            if i in recommended_articles:
                nodecolor.append('#7F00FF')
            else:
                nodecolor.append('#000000')

        for i in graph.nodes:
            if i not in recommended_articles:
                labeldict.pop(i)

        def find_key(val):
            for key, value in labeldict.items():
                if val == value:
                    return key
        exist = []
        with open('Results.csv', 'w', encoding='UTF16', newline='') as f:
            writer = csv.writer(f)
            for i in range(len(df['title'])):
                if df['title'][i] in labeldict.values():
                    if df['title'][i]not in exist:
                        exist.append(df['title'][i])
                        print(find_key(df['title'][i]),df['title'][i], df['url'][i])
                        data = [find_key(df['title'][i]),df['title'][i], df['url'][i]]
                        writer.writerow(data)


        nodesize = []
        for i in graph.nodes:
            if i in recommended_articles:
                nodesize.append(500)
            else:
                nodesize.append(200)

        graph_visualization(graph, position=pos, nodecolor=nodecolor,
                   nodesize=nodesize, title='Graph Theory Result', **kwargs)


    # exclusive content may share no common words with others
    # we still need the last puzzle to get the output
    output = add_non_connected(df, recommended_articles, graph)

    # return the selected articles in a dataframe format
    data = df.loc[[i for i in set(output)]]
    data.reset_index(inplace=True, drop=True)
    del data['word']
    return data, pos
