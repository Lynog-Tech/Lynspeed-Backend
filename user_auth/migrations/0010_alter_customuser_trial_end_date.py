# Generated by Django 5.0.6 on 2024-08-19 14:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0009_alter_customuser_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 20, 15, 23, 43, 315740)),
        ),
    ]
