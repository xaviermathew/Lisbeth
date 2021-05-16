from django.contrib import admin

# Register your models here.
from lisbeth.profile.models import Profile, Photo


class PhotoInline(admin.StackedInline):
    model = Photo


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
