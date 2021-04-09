# Generated by Django 3.1.4 on 2021-04-05 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0022_remove_optionsymbol_optionsportfolio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocksymbol',
            name='asset',
            field=models.CharField(choices=[('ADMIE', 'ADMIE'), ('ALPHA', 'ALPHA'), ('BELA', 'JUMBO'), ('CENER', 'CENERGY'), ('EEE', 'COCA-COLA'), ('ELLAKTOR', 'ELLAKTOR'), ('ELPE', 'ELPE'), ('ETE', 'ETE'), ('EUROB', 'EUROBANK'), ('EXAE', 'EXAE'), ('EYDAP', 'EYDAP'), ('FOYRK', 'FOURLIS'), ('GEKTERNA', 'GEKTERNA'), ('HTO', 'OTE'), ('INLOT', 'INTRALOT'), ('INTRK', 'INTRACOM'), ('LAMDA', 'LAMDA'), ('MIG', 'MIG'), ('MOH', 'MOTOR OIL'), ('MYTIL', 'MYTIL'), ('OPAP', 'OPAP'), ('PPA', 'OLP'), ('PPC', 'DEH'), ('TATT', 'ATTICA BANK'), ('TENERGY', 'TERNA ENERGY'), ('TITC', 'TITAN'), ('TPEIR', 'PEIRAIOS'), ('VIO', 'VIOHALCO')], max_length=10),
        ),
    ]
