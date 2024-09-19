# Generated by Django 5.0.6 on 2024-09-18 18:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionBank', '0009_userresponse_is_correct'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSubjectPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_subjects', models.ManyToManyField(related_name='user_preferences', to='questionBank.subject')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subject_preference', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]