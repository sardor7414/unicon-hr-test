# Generated by Django 4.2.7 on 2023-12-25 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trello', '0004_todo_org_id_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='todo',
            name='org_id_number',
        ),
    ]
