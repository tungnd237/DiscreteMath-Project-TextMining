from scrapy.crawler import CrawlerProcess
from crawler.spiders.vnexpress import VnexpressSpider

fileVariable = open(r'data/vnexpress.csv', 'r+')
fileVariable.truncate(0)
fileVariable.close()

process = CrawlerProcess()
process.crawl(VnexpressSpider)
process.start(stop_after_crawl=True)
