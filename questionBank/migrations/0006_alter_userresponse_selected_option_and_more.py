# Generated by Django 5.0.6 on 2024-08-19 12:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionBank', '0005_worksheet_question_worksheet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userresponse',
            name='selected_option',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=1),
        ),
        migrations.AlterField(
            model_name='question',
            name='correct_option',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default=1, max_length=1),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['order']},
        ),
        migrations.RemoveField(
            model_name='question',
            name='subject',
        ),
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/'),
        ),
        migrations.AddField(
            model_name='question',
            name='option_a',
            field=models.CharField(default='Option A', max_length=255),
        ),
        migrations.AddField(
            model_name='question',
            name='option_b',
            field=models.CharField(default='Option B', max_length=255),
        ),
        migrations.AddField(
            model_name='question',
            name='option_c',
            field=models.CharField(default='Option C', max_length=255),
        ),
        migrations.AddField(
            model_name='question',
            name='option_d',
            field=models.CharField(default='Option D', max_length=255),
        ),
        migrations.AddField(
            model_name='question',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='result',
            name='test_session',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='session_results', to='questionBank.testsession'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='result',
            name='worksheet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='questionBank.worksheet'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userresponse',
            name='test_session',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_responses', to='questionBank.testsession'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='worksheet',
            name='file_path',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='worksheet',
            unique_together={('subject', 'name')},
        ),
        migrations.DeleteModel(
            name='Option',
        ),
    ]