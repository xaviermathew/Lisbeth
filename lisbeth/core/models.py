from django.db import models


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_on', 'updated_on']
        get_latest_by = 'created_on'
