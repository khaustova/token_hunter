# Generated by Django 5.1 on 2025-01-30 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_hunter', '0023_transaction_settings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='boost_max',
            field=models.IntegerField(blank=True, null=True, verbose_name='Максимальное количество boost'),
        ),
        migrations.AddField(
            model_name='settings',
            name='boost_min',
            field=models.IntegerField(blank=True, null=True, verbose_name='Минимальное количество boost'),
        ),
    ]
