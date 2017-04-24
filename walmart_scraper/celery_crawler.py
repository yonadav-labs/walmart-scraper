import sys

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from walmart_scraper.spiders.walmart_spider import WalmartSpider

def scrape_module():
    crawler = CrawlerProcess(get_project_settings())
    crawler.crawl(WalmartSpider, task_id=sys.argv[1])
    crawler.start()

if __name__ == '__main__':
    scrape_module()