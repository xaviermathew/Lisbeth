# Generated by Django 3.1 on 2021-05-15 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0005_profile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_id',
            field=models.CharField(max_length=25, unique=True),
        ),
    ]
