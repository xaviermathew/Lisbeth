from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner

from django.core.management.base import BaseCommand

from lisbeth.core.utils.class_utils import get_object_from_python_path


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--spider',
                            help="Python path to news archive spider",
                            type=str,
                            required=True)

    def handle(self, *args, **options):
        base_class = get_object_from_python_path(options['spider'])
        runner = CrawlerRunner(base_class.get_settings())

        @defer.inlineCallbacks
        def crawl():
            for spider in base_class.get_spider_classes():
                yield runner.crawl(spider)
            reactor.stop()

        crawl()
        reactor.run()
