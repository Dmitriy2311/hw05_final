# Generated by Django 2.2.6 on 2023-01-23 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20221227_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Ссылка на группу'),
        ),
    ]
