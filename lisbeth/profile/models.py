from datetime import datetime
import re

from django.db import models

from lisbeth.core.models import BaseModel


class Profile(models.Model):
    SOURCE_BM = 'b'
    SOURCES = [
        (SOURCE_BM, 'Bethlehem Matrimony')
    ]

    GENDER_M = 'M'
    GENDER_F = 'F'
    GENDER_CHOICES = [
        (GENDER_M, GENDER_M),
        (GENDER_F, GENDER_F),
    ]
    url = models.URLField()
    profile_id = models.CharField(max_length=25, unique=True)
    source = models.CharField(max_length=1, choices=SOURCES)
    data = models.JSONField()

    name = models.TextField()
    age = models.IntegerField(null=True, blank=True)
    dob = models.DateField(null=True)
    marital_status = models.TextField(null=True, blank=True)
    religion = models.TextField(null=True, blank=True)
    diocese = models.TextField(null=True, blank=True)
    parish = models.TextField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    complexion = models.TextField(null=True, blank=True)
    education = models.TextField(null=True, blank=True)
    occupation = models.TextField(null=True, blank=True)
    work_place = models.TextField(null=True, blank=True)
    native_place = models.TextField(null=True, blank=True)
    birth_place = models.TextField(null=True, blank=True)
    educated_at = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, null=True, blank=True)
    num_pics = models.IntegerField()

    name_of_firm = models.TextField(null=True, blank=True)
    monthly_income = models.TextField(null=True, blank=True)
    visa_status = models.TextField(null=True, blank=True)

    about_candidate = models.TextField(null=True, blank=True)

    family_root = models.TextField(null=True, blank=True)
    family_status = models.TextField(null=True, blank=True)

    father_name = models.TextField(null=True, blank=True)
    father_house_name = models.TextField(null=True, blank=True)
    father_native_district = models.TextField(null=True, blank=True)
    father_occupation = models.TextField(null=True, blank=True)

    mother_name = models.TextField(null=True, blank=True)
    mother_house_name = models.TextField(null=True, blank=True)
    mother_native_district = models.TextField(null=True, blank=True)
    mother_occupation = models.TextField(null=True, blank=True)

    num_brothers = models.IntegerField(null=True, blank=True)
    num_brothers_unmarried = models.IntegerField(null=True, blank=True)
    num_sisters = models.IntegerField(null=True, blank=True)
    num_sisters_unmarried = models.IntegerField(null=True, blank=True)
    siblings_description = models.TextField(null=True, blank=True)

    expected_education = models.TextField(null=True, blank=True)
    expected_employment = models.TextField(null=True, blank=True)
    considering_religion = models.TextField(null=True, blank=True)
    partner_description = models.TextField(null=True, blank=True)
    expectations_about_partner =  models.TextField(null=True, blank=True)
    looking_for = models.TextField(null=True, blank=True)

    last_login = models.DateField()
    is_expired = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            ('source', 'profile_id'),
            ('url',)
        )

    def __str__(self):
        return '%s:%s - %s' % (self.get_source_display(), self.profile_id, self.name)

    @staticmethod
    def _clean_name(name):
        if name is None:
            return

        name = re.sub('^Miss\.? ', '', name)
        name = re.sub('^Mr\.? ', '', name)
        name = re.sub('^Dr\.? ', '', name)
        name = re.sub('^Doctor ', '', name)
        name = re.sub('^Adv\.? ', '', name)
        name = re.sub('^Advocate ', '', name)
        name = re.sub('^Ar\.? ', '', name)
        name = re.sub('^Architect ', '', name)
        return name

    @staticmethod
    def _clean_height_weight(s):
        if s is not None:
            try:
                return int(s.split(' ')[0])
            except ValueError:
                pass

    def process_bm(self):
        d = self.data
        self.name = self._clean_name(d['Name'])
        age, marital_status = d['Age / Marital Status'].split('/')
        self.age = int(age.split(' ')[0])
        self.marital_status = marital_status.strip()
        self.religion = d['Religion']
        self.diocese = d['Diocese']
        if 'Height' in d:
            height = self._clean_height_weight(d['Height'])
            weight = None
        else:
            height, weight = d['Height / Weight'].split('/')
            height = self._clean_height_weight(height)
            weight = self._clean_height_weight(weight)
        self.height = height
        self.weight = weight
        self.complexion = d['Complexion']
        self.education = d['Education']
        self.occupation = d['Occupation']
        self.work_place = d['Work Place']
        self.looking_for = d['Looking for']
        self.gender = d['gender']
        self.num_pics = int(d['num_pics'])
        self.last_login = datetime.strptime(d['last_login'], '%d/%m/%Y')
        self.is_expired = d['is_expired']

    def process(self):
        if self.source == self.SOURCE_BM:
            self.process_bm()
        else:
            raise ValueError('unknown source')


class Photo(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.deletion.CASCADE)
    url = models.URLField()
    thumb_url = models.URLField()

    def __str__(self):
        return self.profile.profile_id
