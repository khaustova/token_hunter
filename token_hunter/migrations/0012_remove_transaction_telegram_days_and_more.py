# Generated by Django 5.1 on 2024-11-20 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_hunter', '0011_transaction_is_telegram_error_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='telegram_days',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='telegram_is_scam',
        ),
        migrations.AddField(
            model_name='transaction',
            name='boosts',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Буст'),
        ),
    ]