

# -*- coding: utf-8 -*-
import scrapy
import dateparser
import csv


class LaodongSpider(scrapy.Spider):
    name = 'laodong'
    allowed_domains = ['laodong.vn']
    start_urls = [
        'https://laodong.vn/the-thao/',
        'https://laodong.vn/kinh-te/',
        'https://laodong.vn/the-gioi/',
        'https://laodong.vn/van-hoa-giai-tri/',
        'https://laodong.vn/thoi-su/'
    ]

    def parse(self, response):
        details_links = response.css(
            'li article.article-large header a::attr(href)')
        yield from response.follow_all(details_links, self.parse_detail)

        #pagination_link = response.css(
            #'ul.pagination li.active + li a::attr(href)')
        #yield from response.follow_all(pagination_link, self.parse)

    def parse_detail(self, response):
        metaTitle = response.css(
            'meta[property="og:title"]').re(r'content="(.*)">')
        metaDesc = response.css(
            'meta[name="description"]').re(r'content="(.*)">')

        data = {
            'source': response.url.split("/")[2],
            'url': response.url,
            'title': metaTitle[0] if len(metaTitle) > 0 else '',
            'sapo': metaDesc[0] if len(metaDesc) > 0 else '',
            'tags': response.css('.keywords a::text').getall(),
            'cates': [x.strip() for x in response.css('.breadcrumb a::text').getall()],
            'publish': dateparser.parse(response.css('.time time::text').get().strip()),
            'body': ''.join([x.strip() for x in response.css('.article-content p *::text').getall()])
        }

        with open("webscraping/data/laodong.csv", "a", encoding='utf-8') as dataset:
            writer = csv.writer(dataset)
            #header = ['category', 'url', 'title', 'text']
            #writer.writerow(header)

            writer.writerow([data['title'], data['url']])

        return data
