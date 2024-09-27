# Generated by Django 5.1 on 2024-09-24 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cointer', '0004_alter_transaction_selling_coin_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='buying_total_transactions',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество транзакций на момент покупки'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_total_transfers',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество трансферов на момент покупки'),
        ),
    ]