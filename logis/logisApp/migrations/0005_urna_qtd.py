# Generated by Django 5.0.6 on 2024-06-06 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logisApp', '0004_alter_zonaeleitoral_qtdsecoes'),
    ]

    operations = [
        migrations.AddField(
            model_name='urna',
            name='qtd',
            field=models.IntegerField(default=0),
        ),
    ]