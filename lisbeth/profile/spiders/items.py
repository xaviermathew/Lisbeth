import scrapy
from django.db import IntegrityError
from scrapy.exceptions import DropItem

from lisbeth.profile.models import Profile


class ProfileItem(scrapy.Item):
    url = scrapy.Field()
    profile_id = scrapy.Field()
    source = scrapy.Field()
    data = scrapy.Field()


class ProfileItemPipeline(object):
    def process_item(self, item, spider):
        uid = '%s:%s' % (item['source'], item['url'])
        profile = Profile(**item)
        profile.process()
        try:
            profile.save()
        except IntegrityError as ex:
            if 'duplicate key value violates unique constraint' in ex.args[0]:
                raise DropItem('Profile with uid:[%s] exists' % uid)
            else:
                raise ex
        else:
            spider.log('Profile created with uid:[%s]' % uid)
