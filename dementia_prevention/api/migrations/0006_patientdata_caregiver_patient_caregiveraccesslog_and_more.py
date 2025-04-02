# Generated by Django 5.1.5 on 2025-04-01 03:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_lifestyledata_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('age', models.IntegerField()),
                ('medical_history', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Caregiver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_number', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birth_date', models.DateField()),
                ('conditions', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CaregiverAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_time', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=200)),
                ('caregiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.caregiver')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.patient')),
            ],
        ),
        migrations.AddField(
            model_name='caregiver',
            name='patients',
            field=models.ManyToManyField(related_name='caregivers', to='api.patient'),
        ),
        migrations.CreateModel(
            name='PendingVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verification_code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('caregiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.caregiver')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.patient')),
            ],
        ),
    ]
