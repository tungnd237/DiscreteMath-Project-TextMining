"""
vnexpress crawler.
"""
import json
import csv
import scrapy

def get_urls(pages=30):
    """Get urls for vnexpress categories. Each category may span hundreds of pages.    
    """
    root_urls = [
        "https://vnexpress.net/the-gioi/tu-lieu",
        "https://vnexpress.net/the-gioi/phan-tich",
        "https://vnexpress.net/kinh-doanh/quoc-te",
        "https://vnexpress.net/kinh-doanh/doanh-nghiep",
        "https://vnexpress.net/kinh-doanh/bat-dong-san",
        "https://vnexpress.net/kinh-doanh/vi-mo",
        "https://vnexpress.net/giai-tri/gioi-sao",
        "https://vnexpress.net/giai-tri/phim",
        "https://vnexpress.net/giai-tri/sach",
        "https://vnexpress.net/bong-da",
        "https://vnexpress.net/the-thao/tennis",
        "https://vnexpress.net/the-thao/cac-mon-khac"
    ]

    urls = []
    for root_url in root_urls:
        urls.append(root_url)
        for page in range(1, pages, 1):
            urls.append(root_url + f"-p{page}")

    print(len(urls))
    return urls


class VnexpressSpider(scrapy.Spider):
    name = 'vnexpress'
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/vnexpress.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_EXPORT_INDENT': 4,
    }

    start_urls = get_urls(pages=1)

    def parse(self, response):
        with open("webscraping/data/vnexpress.csv", "a", encoding='utf-8') as dataset:
            writer = csv.writer(dataset)
            header = ['category','url', 'title', 'text']
            writer.writerow(header)

            category = response._url
            for article in response.xpath('//article'):
                writer.writerow([category,article.xpath('div/a/@href').get(), article.xpath('div/a/@title').get(), article.xpath('p/a/text()').get()])
