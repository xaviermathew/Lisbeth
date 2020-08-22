from datetime import datetime
import re

from django.db import models

# Create your models here.
class Profile(models.Model):
    SOURCE_BM = 'b'
    SOURCES = [
        (SOURCE_BM, 'Bethlehem Matrimony')
    ]

    url = models.URLField()
    profile_id = models.CharField(max_length=25)
    source = models.CharField(max_length=1, choices=SOURCES)
    data = models.JSONField()

    name = models.TextField()
    age = models.IntegerField(null=True, blank=True)
    marital_status = models.TextField(null=True, blank=True)
    religion = models.TextField(null=True, blank=True)
    diocese = models.TextField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    complexion = models.TextField(null=True, blank=True)
    education = models.TextField()
    occupation = models.TextField(null=True, blank=True)
    work_place = models.TextField(null=True, blank=True)
    looking_for = models.TextField(null=True, blank=True)
    num_pics = models.IntegerField()
    last_login = models.DateField()
    is_expired = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            ('source', 'profile_id'),
            ('url',)
        )

    def __str__(self):
        return '%s:%s - %s' % (self.get_source_display(), self.profile_id, self.name)

    def process_bm(self):
        d = self.data
        name = d['Name']
        name = re.sub('^Miss\.? ', '', name)
        name = re.sub('^Mr\.? ', '', name)
        name = re.sub('^Dr\.? ', '', name)
        name = re.sub('^Doctor ', '', name)
        name = re.sub('^Adv\.? ', '', name)
        name = re.sub('^Advocate ', '', name)
        self.name = name
        age, marital_status = d['Age / Marital Status'].split('/')
        self.age = int(age.split(' ')[0])
        self.marital_status = marital_status.strip()
        self.religion = d['Religion']
        self.diocese = d['Diocese']
        if 'Height' in d:
            height = int(d['Height'].split(' ')[0])
            weight = None
        else:
            height, weight = d['Height / Weight'].split('/')
            height = int(height.split(' ')[0])
            weight = int(weight.strip().split(' ')[0])
        self.height = height
        self.weight = weight
        self.complexion = d['Complexion']
        self.education = d['Education']
        self.occupation = d['Occupation']
        self.work_place = d['Work Place']
        self.looking_for = d['Looking for']
        self.num_pics = int(d['num_pics'])
        self.last_login = datetime.strptime(d['last_login'], '%d/%m/%Y')

    def process(self):
        if self.source == self.SOURCE_BM:
            self.process_bm()
        else:
            raise ValueError('unknown source')
