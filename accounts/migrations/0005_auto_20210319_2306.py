# Generated by Django 3.1.4 on 2021-03-19 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_portfoliofuture_portfoliostock'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoliooption',
            name='buysellprice',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfoliooption',
            name='contracts',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfoliooption',
            name='position',
            field=models.CharField(choices=[('Long', 'Long'), ('Short', 'Short')], default='Long', max_length=5),
            preserve_default=False,
        ),
    ]
