import json
import os

from scrapy.selector import Selector
from tqdm import tqdm


def _get_data_for_profile_id(base_dir, profile_id):
    d = {
        'photos': [],
        'thumbnails': [],
        'profile_id': 'https://www.bethlehemmatrimonial.com/profile/' + profile_id
    }

    try:
        preview_data = json.load(open(base_dir + 'download_cache/preview/%s.json' % profile_id))
    except IOError:
        preview_data = {}

    photos = preview_data.get('photos', [])
    if isinstance(photos, dict):
        photos = photos.values()
    for fname in photos:
        d['photos'].append({
            'url': 'https://www.bethlehemmatrimonial.com/bethphotos/big/%s' % fname,
            'thumb_url': 'https://www.bethlehemmatrimonial.com/bethphotos/thumb/m/%s' % fname
        })

    try:
        html = open(base_dir + 'download_cache/detail/%s.html' % profile_id).read()
    except IOError:
        return

    selector = Selector(text=html)
    expired = selector.xpath('/html/body/div[2]/div[3]/h2/text()').getall()
    if 'Sorry, this profile validity expired on' in expired or 'is your same gender' in expired:
        return

    d['bm_internal_id'] = selector.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/div[3]/input[1]/@id').get()
    if d['bm_internal_id']:
        d['bm_internal_id'] = d['bm_internal_id'].split('-')[1]
    primary_d = d['primary_details'] = {}
    primary_d['name'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[1]/div[3]/text()'
    primary_d['gender'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[2]/div[3]/text()'
    primary_d['height'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[3]/div[3]/text()'
    primary_d['weight'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[3]/div[6]/text()'
    primary_d['complexion'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[4]/div[3]/text()'
    primary_d['blood_group'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[4]/div[6]/text()'
    primary_d['religion'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[5]/div[3]/text()'
    primary_d['diocese'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[5]/div[6]/text()'
    primary_d['parish'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[6]/div[3]/text()'
    primary_d['native_place'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[6]/div[6]/text()'
    primary_d['birth_place'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[7]/div[3]/text()'
    primary_d['educated_at'] = '//*[@id="profile"]/div[2]/div[1]/div[2]/div[7]/div[6]/text()'

    ed_d = d['education'] = {}
    ed_d['education'] = '//*[@id="profile"]/div[2]/div[3]/div[2]/div[1]/div[3]/text()'
    ed_d['occupation'] = '//*[@id="profile"]/div[2]/div[3]/div[2]/div[2]/div[3]/text()'
    ed_d['name_of_firm'] = '//*[@id="profile"]/div[2]/div[3]/div[2]/div[3]/div[3]/text()'
    ed_d['work_place'] = '//*[@id="profile"]/div[2]/div[3]/div[2]/div[4]/div[3]/text()'
    ed_d['monthly_income'] = '//*[@id="profile"]/div[2]/div[3]/div[2]/div[5]/div[3]/text()'
    ed_d['visa_status'] = '//*[@id="profile"]/div[2]/div[3]/div[2]/div[6]/div[3]/text()'

    d['about_candidate'] = '//*[@id="profile"]/div[2]/div[4]/div[2]/div/text()'

    fam_d = d['family'] = {}
    fam_d['family_root'] = '//*[@id="profile"]/div[2]/div[5]/div[2]/div/div[3]/text()'
    fam_d['family_status'] = '//*[@id="profile"]/div[2]/div[5]/div[2]/div/div[6]/text()'

    father_d = d['father'] = {}
    father_d['name'] = '//*[@id="profile"]/div[2]/div[5]/div[3]/div[2]/div[3]/text()'
    father_d['house_name'] = '//*[@id="profile"]/div[2]/div[5]/div[3]/div[3]/div[3]/text()'
    father_d['native_district'] = '//*[@id="profile"]/div[2]/div[5]/div[3]/div[4]/div[3]/text()'
    father_d['occupation'] = '//*[@id="profile"]/div[2]/div[5]/div[3]/div[5]/div[3]/text()'

    mother_d = d['mother'] = {}
    mother_d['name'] = '//*[@id="profile"]/div[2]/div[5]/div[3]/div[2]/div[6]/text()'
    mother_d['house_name'] = '//*[@id="profile"]/div[2]/div[5]/div[3]/div[3]/div[6]/text()'
    mother_d['native_district'] = '//*[@id="profile"]/div[2]/div[5]/div[3]/div[4]/div[6]/text()'
    mother_d['occupation'] = '//*[@id="profile"]/div[2]/div[5]/div[3]/div[5]/div[6]/text()'

    sib_d = d['siblings'] = {}
    sib_d['num_brothers'] = '//*[@id="profile"]/div[2]/div[6]/div[2]/div[1]/div[3]/text()'
    sib_d['num_sisters'] = '//*[@id="profile"]/div[2]/div[6]/div[2]/div[2]/div[3]/text()'
    sib_d['description'] = '//*[@id="profile"]/div[2]/div[6]/div[3]/div/text()'

    partner_pref_d = d['partner_preferences'] = {}
    partner_pref_d['expected_education '] = '//*[@id="profile"]/div[2]/div[7]/div[2]/div[1]/div[3]/text()'
    partner_pref_d['expected_employment'] = '//*[@id="profile"]/div[2]/div[7]/div[2]/div[2]/div[3]/text()'
    partner_pref_d['considering_religion'] = '//*[@id="profile"]/div[2]/div[7]/div[2]/div[3]/div[3]/text()'
    partner_pref_d['description'] = '//*[@id="profile"]/div[2]/div[7]/div[3]/div/text()'

    d['expectations_about_partner'] = '//*[@id="profile"]/div[2]/div[8]/div[2]/div/text()'

    def get_value(xpath):
        node = selector.xpath(xpath).get()
        if node:
            return node.strip()

    for k, v in d.items():
        if isinstance(v, str) and v.startswith('/'):
            d[k] = get_value(v)
        elif isinstance(v, dict):
            for k1, v1 in v.items():
                if isinstance(v1, str) and v1.startswith('/'):
                    v[k1] = get_value(v1)
                elif isinstance(v1, dict):
                    for k2, v2 in v1.items():
                        if v2.startswith('/'):
                            v1[k2] = get_value(v2)
    return d


def get_data_for_profile_id(base_dir, profile_id):
    from lisbeth.profile.models import Profile

    raw_d = _get_data_for_profile_id(base_dir, profile_id) or {}
    d = {
        'about_candidate': raw_d.get('about_candidate'),
        'expectations_about_partner': raw_d.get('expectations_about_partner')
    }
    primary_d = raw_d.get('primary_details', {})
    if primary_d:
        d['name'] = Profile._clean_name(primary_d['name'])
        d['gender'] = primary_d['gender'][:1] if primary_d['gender'] else None
        d['height'] = Profile._clean_height_weight(primary_d['height'])
        d['weight'] = Profile._clean_height_weight(primary_d['weight'])
        for k in ['complexion', 'blood_group', 'religion', 'diocese', 'native_place', 'birth_place', 'educated_at']:
            d[k] = primary_d[k]

    for section in ['education', 'family', 'father', 'mother', 'partner_preferences']:
        section_d = raw_d.get(section, {})
        if section_d:
            for k, v in section_d.items():
                if section in ['father', 'mother']:
                    k = section + '_' + k
                d[k] = v

    sib_d = raw_d.get('siblings', {})
    if sib_d:
        d['num_brothers'] = 0
        d['num_brothers_unmarried'] = 0
        if sib_d['num_brothers'] and not sib_d['num_brothers'].startswith('No '):
            parts = sib_d['num_brothers'].split()
            d['num_brothers'] = int(parts[0])
            d['num_brothers_unmarried'] = int(parts[1][1:])

        d['num_sisters'] = 0
        d['num_sisters_unmarried'] = 0
        if sib_d['num_sisters'] and not sib_d['num_sisters'].startswith('No '):
            parts = sib_d['num_sisters'].split()
            d['num_sisters'] = int(parts[0])
            d['num_sisters_unmarried'] = int(parts[1][1:])
        d['siblings_description'] = sib_d['description']
    return d


def load_bm_otc_for_profile_id(base_dir, profile_id):
    from lisbeth.profile.models import Profile, Photo

    d = get_data_for_profile_id(base_dir, profile_id)
    attrs = {k: v for k, v in d.items() if v is not None}
    profile, _created = Profile.objects.update_or_create(source=Profile.SOURCE_BM, profile_id=profile_id, defaults=attrs)
    for photo_d in d.get('photos', []):
        Photo.objects.get_or_create(profile=profile, url=photo_d['url'], thumb_url=photo_d['thumb_url'])


def load_bm_otc(base_dir):
    profile_ids = set()
    for fname in os.listdir(base_dir + 'download_cache/preview/'):
        profile_ids.add(fname.split('.')[0])
    for fname in os.listdir(base_dir + 'download_cache/detail/'):
        profile_ids.add(fname.split('.')[0])

    for profile_id in tqdm(profile_ids):
        load_bm_otc_for_profile_id(base_dir, profile_id)
