# Generated by Django 3.2.5 on 2021-10-02 10:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0029_auto_20210815_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='optionseries',
            name='created_at',
            field=models.DateField(auto_now_add=True, default=datetime.datetime(2021, 10, 1, 13, 47, 42, 884336)),
            preserve_default=False,
        ),
    ]
