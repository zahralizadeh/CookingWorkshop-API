# Generated by Django 3.0.5 on 2020-09-04 04:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20200904_0407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='crowled_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 4, 4, 9, 15, 115352, tzinfo=utc)),
        ),
    ]
