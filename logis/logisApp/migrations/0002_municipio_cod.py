# Generated by Django 5.0.6 on 2024-07-16 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logisApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='municipio',
            name='cod',
            field=models.CharField(default=1, max_length=8),
            preserve_default=False,
        ),
    ]
