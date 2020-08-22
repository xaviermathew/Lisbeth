from django.contrib import admin

# Register your models here.
from lisbeth.profile.models import Profile

@admin.register(Profile)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'height', 'weight', 'complexion', 'education', 'occupation', 'work_place', 'num_pics']
    list_filter = ['marital_status', 'religion', 'diocese', 'complexion', 'work_place', 'last_login', 'is_expired', 'num_pics']
