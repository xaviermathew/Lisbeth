# Generated by Django 3.1 on 2020-08-22 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('profile_id', models.CharField(max_length=25)),
                ('source', models.CharField(choices=[('b', 'Bethlehem Matrimony')], max_length=1)),
                ('data', models.JSONField()),
                ('name', models.TextField()),
                ('age', models.IntegerField()),
                ('marital_status', models.TextField()),
                ('religion', models.TextField()),
                ('diocese', models.TextField()),
                ('height', models.IntegerField()),
                ('weight', models.IntegerField()),
                ('complexion', models.TextField()),
                ('education', models.TextField()),
                ('occupation', models.TextField()),
                ('work_place', models.TextField()),
                ('looking_for', models.TextField()),
                ('num_pics', models.TextField()),
                ('last_login', models.DateField()),
                ('is_expired', models.BooleanField(default=False)),
            ],
            options={
                'unique_together': {('url',), ('source', 'profile_id')},
            },
        ),
    ]
