# Generated by Django 5.0.6 on 2024-08-17 19:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0005_alter_customuser_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 18, 20, 34, 23, 529002)),
        ),
    ]
