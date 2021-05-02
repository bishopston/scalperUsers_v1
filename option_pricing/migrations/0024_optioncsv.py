# Generated by Django 3.1.4 on 2021-05-02 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0023_auto_20210405_1240'),
    ]

    operations = [
        migrations.CreateModel(
            name='Optioncsv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trading_symbol', models.CharField(max_length=15)),
                ('date', models.DateTimeField()),
                ('closing_price', models.DecimalField(decimal_places=3, max_digits=8)),
                ('change', models.DecimalField(decimal_places=2, max_digits=10)),
                ('volume', models.IntegerField()),
                ('max', models.DecimalField(decimal_places=3, max_digits=8)),
                ('min', models.DecimalField(decimal_places=3, max_digits=8)),
                ('trades', models.IntegerField()),
                ('fixing_price', models.DecimalField(decimal_places=3, max_digits=8)),
                ('open_interest', models.IntegerField()),
            ],
        ),
    ]