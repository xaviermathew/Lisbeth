from django.contrib import admin
from django.utils.html import mark_safe

from lisbeth.profile.models import Profile, Photo


class PhotoInline(admin.StackedInline):
    model = Photo
    extra = 0
    exclude = ['url', 'thumb_url']
    readonly_fields = ['img_tag']

    def img_tag(self, photo):
        if photo.url:
            return mark_safe('<img src="%s" style="max-width: 350px; max-height: 350px;"/>' % photo.url)
        else:
            return ''


@admin.register(Profile)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ['profile_id', 'name']
    list_display = [
        'profile_id', 'name', 'age', 'height', 'weight',
        'complexion', 'education', 'occupation', 'work_place'
    ]
    list_filter = [
        'marital_status', 'religion', 'gender', 'complexion',
        'last_login', 'is_expired', 'num_pics', 'diocese',
        'work_place', 'family_status'
    ]
    inlines = [PhotoInline]
