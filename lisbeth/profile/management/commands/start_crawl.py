from django.core.management.base import BaseCommand

from scrapy.crawler import CrawlerProcess
from lisbeth.core.utils.class_utils import get_object_from_python_path


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--spider',
                            help="Python path to news archive spider",
                            type=str,
                            required=True)

    def handle(self, *args, **options):
        base_class = get_object_from_python_path(options['spider'])
        process = CrawlerProcess(base_class.get_settings())
        for spider_class in base_class.get_spider_classes():
            process.crawl(spider_class)
        process.start()
