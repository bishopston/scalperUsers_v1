# Generated by Django 3.2.5 on 2021-08-14 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0027_auto_20210814_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='delta',
            field=models.FloatField(default=None),
        ),
        migrations.AlterField(
            model_name='option',
            name='gamma',
            field=models.FloatField(default=None),
        ),
        migrations.AlterField(
            model_name='option',
            name='theta',
            field=models.FloatField(default=None),
        ),
        migrations.AlterField(
            model_name='option',
            name='vega',
            field=models.FloatField(default=None),
        ),
    ]
