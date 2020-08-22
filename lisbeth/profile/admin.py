from django.contrib import admin

# Register your models here.
from lisbeth.profile.models import Profile

@admin.register(Profile)
class PersonAdmin(admin.ModelAdmin):
    pass
