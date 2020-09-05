from django.core.management.base import BaseCommand

from scrapy.crawler import CrawlerProcess
from lisbeth.core.utils.class_utils import get_object_from_python_path


def start_sequentially(process: CrawlerProcess, crawlers: list):
    print('start crawler {}'.format(crawlers[0].__name__))
    deferred = process.crawl(crawlers[0])
    if len(crawlers) > 1:
        deferred.addCallback(lambda _: start_sequentially(process, crawlers[1:]))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--spider',
                            help="Python path to news archive spider",
                            type=str,
                            required=True)

    def handle(self, *args, **options):
        base_class = get_object_from_python_path(options['spider'])
        process = CrawlerProcess(base_class.get_settings())
        start_sequentially(process, base_class.get_spider_classes())
        process.start()
