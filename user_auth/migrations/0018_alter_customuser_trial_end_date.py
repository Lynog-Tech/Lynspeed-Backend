# Generated by Django 5.0.6 on 2024-09-18 18:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0017_alter_customuser_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 19, 19, 56, 3, 647498)),
        ),
    ]