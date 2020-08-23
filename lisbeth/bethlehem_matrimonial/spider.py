import copy
from datetime import datetime

import scrapy
from scrapy.utils.project import get_project_settings

from django.conf import settings

from lisbeth.profile.models import Profile
from lisbeth.core.utils.class_utils import get_python_path
from lisbeth.profile.spiders.items import ProfileItemPipeline, ProfileItem


class BaseBMSpider(scrapy.Spider):
    @staticmethod
    def get_settings():
        d = get_project_settings()
        d['LOG_LEVEL'] = 'INFO'
        d['ITEM_PIPELINES'] = {get_python_path(ProfileItemPipeline): 100}
        d['DOWNLOADER_MIDDLEWARES'] = {'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 100}
        d['HTTPCACHE_ENABLED'] = True
        d['HTTPCACHE_DIR'] = 'data'
        d['ROBOTSTXT_OBEY'] = False
        return d

    def get_extra_profile_data(self):
        return {}

    def _parse_profile_container(self, response, container):
        beth_id = container.xpath('div[2]/div[2]').attrib['id'].split('-')[-1]
        gallery = container.xpath('div[1]/div[contains(@id, "gal-")]')
        bm_internal_id = gallery.attrib['id'].split('gal-')[1].strip()
        last_login = container.xpath('div[1]/p/text()').get().strip()
        d = {
            'url': response.urljoin('/profile/%s' % beth_id),
            'source': Profile.SOURCE_BM,
            'profile_id': beth_id,
            'data': {
                'last_login': last_login,
                'bm_internal_id': bm_internal_id,
                'num_pics': int(gallery.xpath('div/span[1]/text()').get().strip()),
            },
        }
        d['data'].update(self.get_extra_profile_data())
        for row in container.xpath('div[2]/div[1]/div'):
            row_parts = row.xpath('*/text()')
            if len(row_parts) == 3:
                k_el, _, v_el = row_parts
                d['data'][k_el.get().strip()] = v_el.get().strip()
            else:
                k_el = row_parts[0]
                d['data'][k_el.get().strip()] = None

        return ProfileItem(**d)


class BMSpider(BaseBMSpider):
    name = 'bethlehem_matrimonial'
    start_id = 78533
    prefix = 'BETH'
    url_pattern = 'https://www.bethlehemmatrimonial.com/matrimony/%s'


    def _make_request(self, id):
        beth_id = '%s%s' % (self.prefix, id)
        url = self.url_pattern % beth_id
        return scrapy.Request(url=url, callback=self.parse, meta={'prev_id': id})

    def start_requests(self):
        yield self._make_request(self.parse)

    # def parse_pics(self, response, **kwargs):
    #     d = response.meta['profile']
    #     r = response.json()
    #     if r['success']:
    #         d['pics'] = r['photos']
    #     else:
    #         d['pics'] = []
    #     yield ProfileItem(url=response.url, **d)

    # def _parse_profile_container(self, response, container):
    #     d = super(BMSpider, self)._parse_profile_container(response, container)
    #     bm_internal_id = d['bm_internal_id']
    #     r = requests.post('https://www.bethlehemmatrimonial.com/ajax-actions',
    #                       data='action=load-gallery&profile_id=%s' % bm_internal_id,
    #                       headers={'X-Requested-With': 'XMLHttpRequest',
    #                                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
    #     pic_url = 'https://www.bethlehemmatrimonial.com/ajax-actions'
    #     payload = {
    #         'action': 'load-gallery',
    #         'profile_id': bm_internal_id
    #     }
    #     yield scrapy.FormRequest(
    #         url=pic_url, method='POST', formdata=payload,
    #         callback=self.parse_pics, meta={'profile': d},
    #         headers={
    #             'X-Requested-With': 'XMLHttpRequest',
    #             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #         }
    #     )

    def parse(self, response, **kwargs):
        container = response.xpath('//*[@id="search-results"]/div/div[2]/div')
        if container:
            yield self._parse_profile_container(response, container)

        yield self._make_request(response.meta['prev_id'] - 1)


class AuthenticatedBMSpider(BaseBMSpider):
    url_pattern = 'https://www.bethlehemmatrimonial.com/profiles?g={gender}&sid=1598116223&p={page}&expired={expired}'
    expired_choices = ['0', '1']
    gender_choices = ['M', 'F']

    @classmethod
    def get_spider_classes(cls):
        spider_classes = []
        for gender in cls.gender_choices:
            for expired in cls.expired_choices:
                class_name = 'Authenticated{gender}{expired}BMSpider'.format(gender=gender, expired=expired)
                spider_name = 'authd_{gender}_{expired}_bethlehem_matrimonial'
                attrs = {
                    'name': spider_name,
                    'crawl_options': {
                        'gender': gender,
                        'expired': expired,
                    },
                    'profile_options': {
                        'gender': gender,
                        'is_expired': bool(int(expired)),
                    },
                    'get_extra_profile_data': lambda self: self.profile_options
                }
                spider_class = type(str(class_name), (cls,), attrs)
                spider_classes.append(spider_class)
        return spider_classes

    def start_requests(self):
        formdata = {
            'login_profile': settings.BM_USERNAME,
            'login_password': settings.BM_PASSWORD,
            'login': 'Login'
        }
        yield scrapy.FormRequest(url='https://www.bethlehemmatrimonial.com/login',
                                 method='POST',
                                 formdata=formdata,
                                 callback=self.get_listing,
                                 meta={'prev_page': 0})

    def get_listing(self, response):
        d = copy.deepcopy(response.meta)
        d['prev_page'] += 1
        page = d['prev_page']
        if not settings.SHOULD_LIMIT_PROFILE_CRAWL or page <= 3:
            url = self.url_pattern.format(page=page, **self.crawl_options)
            yield scrapy.Request(url, callback=self.parse_listing, meta=d)

    def parse_listing(self, response):
        for container in response.xpath('//*[@id="search-results"]/div/div[2]/div'):
            yield self._parse_profile_container(response, container)
        yield from self.get_listing(response)
