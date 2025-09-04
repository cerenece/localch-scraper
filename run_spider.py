from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from pydispatch import dispatcher
from localch.localch.spiders.localch_spider import LocalchSeleniumSpider
from scrapy import signals
import queue

# Sonuçları thread-safe kuyruğa göndereceğiz
results_queue = queue.Queue()

def run_spider_async(keyword):
    def crawler_results(item, response, spider):
        results_queue.put(item)  # Her item geldiğinde kuyruğa ekle

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(LocalchSeleniumSpider, keyword=keyword)
        reactor.stop()

    crawl()
    reactor.run()
