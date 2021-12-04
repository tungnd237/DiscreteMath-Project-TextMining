import newspaper
import webscraping
import webscraping.crawler.spiders.vnexpress as vnexpress
import webscraping.crawler.spiders.dantri as dantri
import webscraping.crawler.spiders.laodong as laodong
from newspaper import Article

webscraping.crawl_data()

article_url_vn= vnexpress.article_url_vi
article_url_dt= vnexpress.article_url_dt

for url in article_url_dt:
    if url != None:
        article = Article(url)
        article.download()
        article.parse()
        print(article.title)
