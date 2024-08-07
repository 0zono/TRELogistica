# Generated by Django 5.0.6 on 2024-07-17 13:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logisApp', '0003_secao'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zona_eleitoral_name', models.CharField(blank=True, max_length=255, null=True)),
                ('quantity', models.PositiveIntegerField()),
                ('distribution_type', models.CharField(choices=[('MRV', 'Primary'), ('CONT', 'Contingency')], max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('distributed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('material_eleitoral', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='logisApp.materialeleitoral')),
                ('urna', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='logisApp.urna')),
                ('zona_eleitoral', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='logisApp.zonaeleitoral')),
            ],
        ),
    ]
