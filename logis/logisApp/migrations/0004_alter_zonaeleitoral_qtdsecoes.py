# Generated by Django 5.0.6 on 2024-06-06 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logisApp', '0003_zonaeleitoral_qtdsecoes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zonaeleitoral',
            name='qtdSecoes',
            field=models.IntegerField(default=0),
        ),
    ]
