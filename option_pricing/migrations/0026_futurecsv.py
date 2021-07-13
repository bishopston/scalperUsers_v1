# Generated by Django 3.1.4 on 2021-05-02 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0025_auto_20210502_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='Futurecsv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=15)),
                ('date', models.DateField()),
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