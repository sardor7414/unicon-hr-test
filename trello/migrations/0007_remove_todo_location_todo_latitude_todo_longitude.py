# Generated by Django 4.2.7 on 2023-12-26 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trello', '0006_alter_todo_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='todo',
            name='location',
        ),
        migrations.AddField(
            model_name='todo',
            name='latitude',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='todo',
            name='longitude',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
