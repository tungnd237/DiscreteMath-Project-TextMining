from scrapy.crawler import CrawlerProcess
from webscraping.crawler.spiders.vnexpress import VnexpressSpider
from webscraping.crawler.spiders.dantri import DantriSpider
from webscraping.crawler.spiders.laodong import LaodongSpider
import csv

def crawl_data():

    fileVariable = open(r'webscraping/data/vnexpress.csv', 'r+')
    fileVariable.truncate(0)
    fileVariable.close()

    fileVariable = open(r'webscraping/data/laodong.csv', 'r+')
    fileVariable.truncate(0)
    fileVariable.close()

    with open("webscraping/data/laodong.csv", "a", encoding='utf-8') as dataset:
        writer = csv.writer(dataset)
        header = ['title', 'text']
        writer.writerow(header)

    process = CrawlerProcess()
    process.crawl(VnexpressSpider)
    process.crawl(LaodongSpider)
    process.start()
