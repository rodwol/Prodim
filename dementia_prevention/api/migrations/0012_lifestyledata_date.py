# Generated by Django 5.1.5 on 2025-04-05 04:19

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_remove_lifestyledata_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lifestyledata',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
