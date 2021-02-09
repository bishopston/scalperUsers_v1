# Generated by Django 3.1.4 on 2021-02-04 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('option_pricing', '0009_auto_20210115_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futuresymbol',
            name='asset',
            field=models.CharField(choices=[('ADMIE', 'ADMIE'), ('ALPHA', 'ALPHA'), ('BELA', 'JUMBO'), ('CENER', 'CENERGY'), ('EEE', 'COCA-COLA'), ('ELLAK', 'ELLAKTOR'), ('ELPE', 'ELPE'), ('ETE', 'ETE'), ('EUROB', 'EUROB'), ('EXAE', 'EXAE'), ('EYDAP', 'EYDAP'), ('FOYRK', 'FOURLIS'), ('FTSE', 'FTSE'), ('GEKTE', 'GEKTERNA'), ('HTO', 'OTE'), ('INLOT', 'INTRALOT'), ('INTRK', 'INTRACOM'), ('LAMDA', 'LAMDA'), ('MIG', 'MIG'), ('MOH', 'MOTOR OIL'), ('MYTIL', 'MYTIL'), ('OPAP', 'OPAP'), ('PPA', 'OLP'), ('PPC', 'DEH'), ('TATT', 'ATTICA BANK'), ('TENER', 'TERNA ENERGY'), ('TITC', 'TITAN'), ('TPEIR', 'PEIRAIOS'), ('VIO', 'VIOHALCO')], max_length=5),
        ),
    ]