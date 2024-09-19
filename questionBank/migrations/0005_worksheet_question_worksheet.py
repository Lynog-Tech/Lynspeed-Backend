# Generated by Django 5.0.6 on 2024-08-17 19:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionBank', '0004_testsession'),
    ]

    operations = [
        migrations.CreateModel(
            name='Worksheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worksheets', to='questionBank.subject')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='worksheet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='questionBank.worksheet'),
            preserve_default=False,
        ),
    ]