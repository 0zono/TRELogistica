# Generated by Django 5.0.6 on 2024-08-01 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logisApp', '0007_solicitacao_delete_ze_solicita_urna'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacao',
            name='distribution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solicitacoes', to='logisApp.distribuicao'),
        ),
    ]