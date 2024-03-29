# Generated by Django 3.2.5 on 2021-08-14 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0026_futurecsv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='delta',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='option',
            name='gamma',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='option',
            name='theta',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='option',
            name='vega',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
    ]
