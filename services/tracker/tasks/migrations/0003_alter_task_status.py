# Generated by Django 4.2.11 on 2024-03-17 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('NEW', 'New'), ('CLOSED', 'Closed')], default='NEW', max_length=10),
        ),
    ]
