# Generated by Django 5.2 on 2025-04-21 14:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicObjective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Nombre del Objetivo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name': 'Objetivo Académico',
                'verbose_name_plural': 'Objetivos Académicos',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('number', models.PositiveSmallIntegerField(choices=[(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')], help_text='Mes (1=Enero, 12=Diciembre)', primary_key=True, serialize=False, verbose_name='Número de Mes')),
            ],
            options={
                'verbose_name': 'Mes',
                'verbose_name_plural': 'Meses',
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='SGCObjective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Nombre del Objetivo SGC')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción SGC')),
            ],
            options={
                'verbose_name': 'Objetivo SGC',
                'verbose_name_plural': 'Objetivos SGC',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='KPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(help_text='El número oficial (1-68) que identifica este KPI.', unique=True, verbose_name='Número de KPI')),
                ('name', models.CharField(help_text='El nombre corto o título del KPI.', max_length=500, verbose_name='Nombre Corto / Título')),
                ('description', models.TextField(blank=True, help_text='Descripción explicando el KPI, su propósito y método de cálculo.', null=True, verbose_name='Descripción Detallada')),
                ('academic_objective', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kpis', to='kpi_list.academicobjective', verbose_name='Objetivo Académico Relacionado')),
                ('review_months', models.ManyToManyField(blank=True, help_text='Seleccione los meses en que este KPI debe ser revisado/reportado.', to='kpi_list.month', verbose_name='Meses de Revisión')),
                ('sgc_objective', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kpis', to='kpi_list.sgcobjective', verbose_name='Objetivo SGC Relacionado')),
            ],
            options={
                'verbose_name': 'KPI',
                'verbose_name_plural': 'KPIs',
                'ordering': ['number'],
            },
        ),
    ]
