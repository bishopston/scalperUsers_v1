# Generated by Django 3.1.4 on 2021-02-07 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0010_auto_20210204_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Optionseries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset', models.CharField(choices=[('FTSE', 'FTSE'), ('ALPHA', 'ALPHA'), ('HTO', 'OTE'), ('ETE', 'ETE'), ('OPAP', 'OPAP'), ('PPC', 'DEH'), ('TPEIR', 'PEIRAIOS')], max_length=5)),
                ('optiontype', models.CharField(choices=[('c', 'Call'), ('p', 'Put')], max_length=1)),
                ('expmonthdate', models.DateField()),
            ],
        ),
    ]
