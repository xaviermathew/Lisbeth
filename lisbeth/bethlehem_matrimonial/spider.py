import copy
from datetime import datetime, timedelta

import scrapy
from scrapy.utils.project import get_project_settings

from django.conf import settings

from lisbeth.core.utils.class_utils import get_python_path
from lisbeth.core.utils.file_utils import mkdir_p
from lisbeth.profile.models import Profile
from lisbeth.profile.spiders.items import ProfileItemPipeline, ProfileItem


class AuthenticatedBMSpider(scrapy.Spider):
    url_pattern = 'https://www.bethlehemmatrimonial.com/profiles?g={gender}&sid={sid}&p={page}&expired={expired}{extra}'
    detail_url_pattern = 'https://www.bethlehemmatrimonial.com/profile/{beth_id}'
    preview_url = 'https://www.bethlehemmatrimonial.com/ajax-actions'
    expired_choices = ['0', '1']
    gender_choices = ['F', 'M']  # ladies first
    extra_choices = ['', '&sl=1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mkdir_p('download_cache/fragments/')
        mkdir_p('download_cache/detail/')
        mkdir_p('download_cache/preview/')

    @staticmethod
    def get_settings():
        d = get_project_settings()
        d['LOG_LEVEL'] = 'INFO'
        d['ITEM_PIPELINES'] = {get_python_path(ProfileItemPipeline): 100}
        d['DOWNLOADER_MIDDLEWARES'] = {'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 100}
        d['HTTPCACHE_ENABLED'] = True
        d['HTTPCACHE_DIR'] = 'data'
        d['ROBOTSTXT_OBEY'] = False
        d['TELNETCONSOLE_PORT'] = None
        return d

    def get_extra_profile_data(self):
        return {}

    def _parse_profile_container(self, response, container):
        beth_id = container.xpath('div[2]/div[2]').attrib['id'].split('-')[-1]
        with open('download_cache/fragments/%s.html' % beth_id, 'w') as f:
            f.write(container.get())

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

    @classmethod
    def get_spider_classes(cls):
        spider_classes = []
        today = datetime.today()
        n_years_ago = today - timedelta(days=3 * 365)
        n_days = 7 * 24 * 60 * 60
        sids = range(int(n_years_ago.timestamp()), int(today.timestamp()), n_days)
        for extra in cls.extra_choices:
            if extra == '&sl=1':
                sid_choices = sids
            else:
                sid_choices = ['']
            pythonified_extra = extra.replace('&', 'and').replace('=', 'equals')
            for gender in cls.gender_choices:
                for expired in cls.expired_choices:
                    for sid in sid_choices:
                        class_name = 'Authenticated{gender}{sid}{expired}{extra}BMSpider'.format(
                            gender=gender,
                            sid=sid,
                            expired=expired,
                            extra=pythonified_extra
                        )
                        spider_name = 'authd_{gender}_{sid}_{expired}_{extra}_bethlehem_matrimonial'.format(
                            gender=gender,
                            sid=sid,
                            expired=expired,
                            extra=pythonified_extra
                        )
                        attrs = {
                            'name': spider_name,
                            'crawl_options': {
                                'gender': gender,
                                'expired': expired,
                                'sid': sid,
                                'extra': extra
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
        if not settings.SHOULD_LIMIT_PROFILE_CRAWL or page <= 2:
            url = self.url_pattern.format(page=page, **self.crawl_options)
            yield scrapy.Request(url, callback=self.parse_listing, meta=d)

    def parse_listing(self, response):
        for container in response.xpath('//*[@id="search-results"]/div/div[2]/div'):
            profile_item = self._parse_profile_container(response, container)
            yield profile_item
            url = self.detail_url_pattern.format(beth_id=profile_item['profile_id'])
            yield scrapy.Request(url, callback=self.parse_detail, meta={'profile_id': profile_item['profile_id']})
            yield scrapy.FormRequest(url=self.preview_url,
                                     callback=self.parse_preview,
                                     method='POST',
                                     formdata={'action': 'load-gallery', 'profile_id': profile_item['data']['bm_internal_id']},
                                     headers={'X-Requested-With': 'XMLHttpRequest'},
                                     meta={'profile_id': profile_item['profile_id']})

        yield from self.get_listing(response)

    def parse_detail(self, response):
        # ed_and_prof = response.xpath('//*[@id="profile"]/div[2]/div[3]/div[2]/div')
        # ed_and_prof = response.xpath('//*[@id="profile"]/div[2]/div[4]/div[2]/div')
        # family_root = response.xpath('//*[@id="profile"]/div[2]/div[5]/div[2]/div')
        # parents_details = response.xpath('//*[@id="profile"]/div[2]/div[5]/div[3]/div[1]')
        # sibling_detail = response.xpath('//*[@id="profile"]/div[2]/div[6]/div[2]/div')
        # sibling_blob = response.xpath('//*[@id="profile"]/div[2]/div[6]/div[3]/div')
        # partner_preferences = response.xpath('//*[@id="profile"]/div[2]/div[7]/div[2]/div[1]')
        # expectations = response.xpath('//*[@id="profile"]/div[2]/div[8]/div[2]/div')
        beth_id = response.meta['profile_id']
        with open('download_cache/detail/%s.html' % beth_id, 'w') as f:
            f.write(response.text)

    def parse_preview(self, response):
        beth_id = response.meta['profile_id']
        with open('download_cache/preview/%s.json' % beth_id, 'w') as f:
            f.write(response.text)
