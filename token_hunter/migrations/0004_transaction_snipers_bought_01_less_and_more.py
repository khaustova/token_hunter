# Generated by Django 5.1 on 2024-10-10 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_hunter', '0003_remove_transaction_buying_transactions_buys_h1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_01_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, купившие меньше, чем на 0.1$'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_01_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие меньше, чем на 0.1$'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='top_traders_bought_01_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, купившие меньше, чем на 0.1$'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='top_traders_sold_01_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, продавшие меньше, чем на 0.1$'),
        ),
    ]