# Generated by Django 5.2 on 2025-04-21 14:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(unique=True, verbose_name='Año')),
                ('start_date', models.DateField(verbose_name='Fecha de Inicio')),
                ('end_date', models.DateField(verbose_name='Fecha de Fin')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Año Académico',
                'verbose_name_plural': 'Años Académicos',
                'ordering': ['-year'],
            },
        ),
        migrations.CreateModel(
            name='GradeLevel',
            fields=[
                ('code', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True, verbose_name='Código')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre Completo')),
                ('stage', models.CharField(choices=[('PRE', 'Preparatorio'), ('PRO', 'Profundización'), ('EXP', 'Expansión')], default='PRE', max_length=3, verbose_name='Etapa')),
                ('order', models.PositiveSmallIntegerField(default=0, help_text='Orden para clasificación (e.g., 1=Pre, 2=Pro, 3=Exp)', verbose_name='Orden')),
            ],
            options={
                'verbose_name': 'Grado',
                'verbose_name_plural': 'Grados',
                'ordering': ['order', 'code'],
            },
        ),
        migrations.CreateModel(
            name='Paralelo',
            fields=[
                ('code', models.CharField(max_length=1, primary_key=True, serialize=False, unique=True, verbose_name='Código')),
                ('name', models.CharField(blank=True, max_length=50, verbose_name='Nombre Descriptivo')),
            ],
            options={
                'verbose_name': 'Paralelo',
                'verbose_name_plural': 'Paralelos',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Periodo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(verbose_name='Número Total')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')),
            ],
            options={
                'verbose_name': 'Periodo',
                'verbose_name_plural': 'Periodos',
                'ordering': ['trimestre__academic_year', 'number'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre Asignatura')),
            ],
            options={
                'verbose_name': 'Asignatura',
                'verbose_name_plural': 'Asignaturas',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Trimestre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(verbose_name='Número')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')),
            ],
            options={
                'verbose_name': 'Trimestre',
                'verbose_name_plural': 'Trimestres',
                'ordering': ['academic_year', 'number'],
            },
        ),
        migrations.CreateModel(
            name='TeacherAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='academics.academicyear', verbose_name='Año Académico')),
                ('grade_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='academics.gradelevel', verbose_name='Grado')),
                ('paralelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='academics.paralelo', verbose_name='Paralelo')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teacher_assignments', to='academics.subject', verbose_name='Asignatura')),
            ],
            options={
                'verbose_name': 'Asignación Docente por Clase',
                'verbose_name_plural': 'Asignaciones Docentes por Clase',
                'ordering': ['academic_year', 'teacher', 'grade_level', 'paralelo'],
            },
        ),
    ]
