# Generated by Django 4.2.7 on 2023-12-26 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trello', '0005_remove_todo_org_id_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='photo',
            field=models.CharField(max_length=5000, verbose_name='Rasm'),
        ),
    ]
