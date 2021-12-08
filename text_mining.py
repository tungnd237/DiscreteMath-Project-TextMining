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

### function

#convert text into a list of words
#we can use stemming and lemmatization to improve efficiency
#for instance, we have words walked,walking,walks
#with nltk package, we can revert all of them to walk
def text2list(text,stopword,lower=True,lemma=False,stemma=False):
    text_clean=text if lower==False else text.lower()
    #tokenize and remove stop words
    token=[i for i in nltk.tokenize.RegexpTokenizer(r'\w+').tokenize(text_clean) if i not in stopword]

    #lemmatization
    if lemma:
        text_processed=[nltk.stem.wordnet.WordNetLemmatizer().lemmatize(i) for i in token]
    else:
        text_processed=token

    #stemming
    if stemma:
        output=[nltk.stem.PorterStemmer().stem(i) for i in text_processed]
    else:
        output=text_processed

    #remove numbers as they are stopword as well
    for i in [ii for ii in output]:
        try:
            float(i)
            output.remove(i)
        except:
            pass
    return [i for i in output if i not in stopword]

#find common words between two texts
#return the number of common words as the weight of the edge
def find_common(text1,text2,stopword):

    common=set(text1).intersection(set(text2)).difference(set(stopword))

    return len(common)

#this is just a function to add one more column in dataframe
#so the dataframe has a column which breaks texts into lists of words
def add_wordlist(df,stopword,**kwargs):

    temp=[]
    #display(df)

    for i in df['title']:
        temp.append(text2list(i,stopword,lower=True,**kwargs))
    df['word']=temp

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
            w = find_common(df['word'][i], df['word'][j], stopword)
            if w != 0:
                labeldict[i] = df['title'][i]
                labeldict[j] = df['title'][j]
                graph.add_edge(i, j, weight=w)

    # print title and postition
    return graph

# plotting the graph structure
def plot_graph(graph, position, nodecolor=[], nodesize=[],
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
def algo(graph):

    #dictionary of all nodes and degrees in graph
    D=dict(graph.degree)

    #order dict by each node's degree
    D=dict(sorted(D.items(),key=lambda x:x[1],reverse=False))

    queue=list(D.keys())
    result=[]

    #in each iteration, find the node with the highest agree in the queue
    #remove the node's neighbors in the queue until the queue is empty
    while queue:

        V=queue.pop()
        result.append(V)

        redundant=set(queue).intersection(set(graph.neighbors(V)))

        for i in redundant:
            queue.remove(i)

    return result

#use graph theory to remove similar content
def remove_similar(df, stopword, plot_original=False,
                   plot_result=False,**kwargs):
    # tokenization
    df = add_wordlist(df, stopword, **kwargs)

    # graph building
    graph = build_graph(df, stopword, **kwargs)

    # fix node position for visual comparison
    pos = nx.spring_layout(graph, k=0.3)

    # plot original
    if plot_original:
        plot_graph(graph, position=pos,
                   title='Original', **kwargs)

    # traversal
    result = algo(graph)

    # plot result, highlight the result
    if plot_result:
        nodecolor = []
        for i in graph.nodes:
            if i in result:
                nodecolor.append(1)
            else:
                nodecolor.append(0)

        for i in graph.nodes:
            if i not in result:
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
            if i in result:
                nodesize.append(400)
            else:
                nodesize.append(200)

        plot_graph(graph, position=pos, nodecolor=nodecolor,
                   nodesize=nodesize, title='Graph Theory Result', **kwargs)


    # exclusive content may share no common words with others
    # we still need the last puzzle to get the output
    output = add_non_connected(df, result, graph)

    # return the selected nodes in a dataframe format
    data = df.loc[[i for i in set(output)]]
    data.reset_index(inplace=True, drop=True)
    del data['word']
    return data, pos
