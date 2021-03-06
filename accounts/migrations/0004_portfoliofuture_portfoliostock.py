# Generated by Django 3.1.4 on 2021-03-18 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0022_remove_optionsymbol_optionsportfolio'),
        ('accounts', '0003_portfoliooption'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('portfolio', models.ManyToManyField(blank=True, default=None, related_name='stocksportfolio', to='accounts.Portfolio')),
                ('stocksymbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='option_pricing.stocksymbol')),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioFuture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('futuresymbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='option_pricing.futuresymbol')),
                ('portfolio', models.ManyToManyField(blank=True, default=None, related_name='futuresportfolio', to='accounts.Portfolio')),
            ],
        ),
    ]
