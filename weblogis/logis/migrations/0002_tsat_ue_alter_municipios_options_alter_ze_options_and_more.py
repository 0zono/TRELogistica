# Generated by Django 5.0.3 on 2024-03-26 14:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TSAT',
            fields=[
                ('modelo', models.CharField(primary_key=True, serialize=False, unique=True)),
                ('quantidade', models.IntegerField()),
                ('bio', models.BooleanField()),
                ('ativo', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='UE',
            fields=[
                ('modelo', models.CharField(primary_key=True, serialize=False, unique=True)),
                ('bio', models.BooleanField()),
                ('ativo', models.BooleanField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='municipios',
            options={'verbose_name_plural': 'Municipios'},
        ),
        migrations.AlterModelOptions(
            name='ze',
            options={'verbose_name': 'ZonaEleitoral', 'verbose_name_plural': 'Zonas Eleitorais'},
        ),
        migrations.RemoveField(
            model_name='ze',
            name='id',
        ),
        migrations.AlterField(
            model_name='ze',
            name='idZE',
            field=models.CharField(max_length=20, primary_key=True, serialize=False, unique=True, verbose_name='identificador da zona eleitoral'),
        ),
        migrations.CreateModel(
            name='Secao',
            fields=[
                ('secao_id', models.AutoField(primary_key=True, serialize=False)),
                ('local_numero', models.IntegerField(verbose_name='Número do local da secao.')),
                ('eletricidade_irregular', models.BooleanField(verbose_name='Eletricidade irregular')),
                ('dificil_acesso', models.BooleanField(verbose_name='Acesso dificil?')),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='secoes', to='logis.municipios')),
            ],
            options={
                'verbose_name': 'secao',
                'verbose_name_plural': 'secoes',
            },
        ),
        migrations.CreateModel(
            name='ZE_solicita_UE',
            fields=[
                ('solicitacao_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('qtd', models.IntegerField()),
                ('mrj', models.BooleanField()),
                ('contingencia', models.BooleanField()),
                ('modelo_ue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logis.ue')),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logis.municipios')),
            ],
        ),
    ]