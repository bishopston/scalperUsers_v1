# Generated by Django 3.1.4 on 2021-01-15 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0008_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stocksymbol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=15)),
                ('asset', models.CharField(choices=[('ADMIE', 'ADMIE'), ('ALPHA', 'ALPHA'), ('BELA', 'JUMBO'), ('CENER', 'CENERGY'), ('GD', 'GD'), ('EEE', 'COCA-COLA'), ('ELLAKTOR', 'ELLAKTOR'), ('ELPE', 'ELPE'), ('ETE', 'ETE'), ('EUROB', 'EUROB'), ('EXAE', 'EXAE'), ('EYDAP', 'EYDAP'), ('FOYRK', 'FOURLIS'), ('FTSE', 'FTSE'), ('GEKTERNA', 'GEKTERNA'), ('HTO', 'OTE'), ('INLOT', 'INTRALOT'), ('INTRK', 'INTRACOM'), ('LAMDA', 'LAMDA'), ('MIG', 'MIG'), ('MOH', 'MOTOR OIL'), ('MYTIL', 'MYTIL'), ('OPAP', 'OPAP'), ('PPA', 'OLP'), ('PPC', 'DEH'), ('TATT', 'ATTICA BANK'), ('TENERGY', 'TERNA ENERGY'), ('TITC', 'TITAN'), ('TPEIR', 'PEIRAIOS'), ('VIO', 'VIOHALCO')], max_length=10)),
            ],
        ),
        migrations.RemoveField(
            model_name='stock',
            name='asset',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='symbol',
        ),
        migrations.AddField(
            model_name='stock',
            name='stocksymbol',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='option_pricing.stocksymbol'),
        ),
    ]
