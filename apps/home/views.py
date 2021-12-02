# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
import os
import config
import text_mining as tm
import pandas as pd
import webscraping


def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def graph(request):
    # data = config.DATA_DIR
    stopwords = config.STOPWORDS
    # os.chdir(data)

    # iterate through all file
    # list_title = []

    # for file in os.listdir():
    # Check whether file is in text format or not
    # if file.endswith(".txt"):
    # file_path = f"{data}\{file}"

    # call read text file function
    # list_title.append(tm.read_text_file(file_path).strip()[:50])

    # df = pd.DataFrame(list_title, columns=['title'])
    # basePath = os.path.dirname(os.path.abspath(__file__))
    # df = pd.read_json(basePath + '\webscraping\data\vnexpress.json', lines = True, orient = "records",encoding = 'utf8'
    # , dtype={"'category'":str, "url":str, "title": str, "text": str})

    webscraping.crawl_data()

    df = pd.read_csv(r'webscraping/data/vnexpress.csv', encoding="utf8")

    df_title = df['title'].copy().dropna()
    df_title = df_title.to_frame()
    df_title = df_title[df_title.title != "title"]

    ### stopword vietnam
    f = open(stopwords, 'r', encoding="utf8")
    stopword_vn = f.read().split('\n')

    ### Run graph
    df_sample = df_title.sample(100, replace=True)
    df_sample = df_sample.reset_index(drop=True)
    output, position = tm.remove_similar(df_sample, stopword_vn, plot_original=True, plot_result=True)
    return render(request, "graph.html")


def pages(request):
    os.system('python3 run_text_mining.py')
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
