# Generated by Django 3.1.4 on 2021-01-02 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0002_auto_20210101_2347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='optionsymbol',
            name='like_count',
        ),
    ]