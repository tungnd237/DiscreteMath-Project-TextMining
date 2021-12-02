from scrapy.crawler import CrawlerProcess
from webscraping.crawler.spiders.vnexpress import VnexpressSpider

def crawl_data():

    fileVariable = open(r'webscraping/data/vnexpress.csv', 'r+')
    fileVariable.truncate(0)
    fileVariable.close()

    process = CrawlerProcess()
    process.crawl(VnexpressSpider)
    process.start(stop_after_crawl=True)
