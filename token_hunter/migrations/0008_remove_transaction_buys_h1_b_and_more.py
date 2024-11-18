# Generated by Django 5.1 on 2024-11-18 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_hunter', '0007_remove_transaction_buys_h1_s_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='buys_h1_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='buys_h24_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='buys_h6_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='buys_m5_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='fdv_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='liquidity_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='market_cap_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='price_change_h1_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='price_change_h24_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='price_change_h6_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='price_change_m5_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sells_h1_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sells_h24_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sells_h6_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sells_m5_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_bought_01_less',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_bought_5000_more',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_no_bought',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_pnl_5000_more',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_pnl_loss',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_pnl_profit',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_sold_01_less',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_sold_5000_more',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_sum_bought',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sns_sum_sold',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='transactions_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_bought_01_less',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_bought_5000_more',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_no_bought',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_no_sold',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_pnl_5000_more',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_pnl_loss',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_pnl_profit',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_sold_01_less',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_sold_5000_more',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_sum_bought',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='tt_sum_sold',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='volume_h1_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='volume_h24_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='volume_h6_b',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='volume_m5_b',
        ),
        migrations.AddField(
            model_name='transaction',
            name='buys_h1',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок (1 час)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buys_h24',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buys_h6',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buys_m5',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок (5 минут)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='fdv',
            field=models.FloatField(blank=True, null=True, verbose_name='FDV'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_mutable_metadata',
            field=models.BooleanField(blank=True, default=True, null=True, verbose_name='Изменяемые метаданные'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='liquidity',
            field=models.FloatField(blank=True, null=True, verbose_name='Ликвидность (5 минут)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='market_cap',
            field=models.FloatField(blank=True, null=True, verbose_name='Рыночная капитализация'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='price_change_h1',
            field=models.FloatField(blank=True, null=True, verbose_name='Изменение цены (1 час)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='price_change_h24',
            field=models.FloatField(blank=True, null=True, verbose_name='Изменение цены (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='price_change_h6',
            field=models.FloatField(blank=True, null=True, verbose_name='Изменение цены (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='price_change_m5',
            field=models.FloatField(blank=True, null=True, verbose_name='Изменение цены (5 минут)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='sells_h1',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж (1 час)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='sells_h24',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='sells_h6',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='sells_m5',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж (5 минут)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transactions',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество транзакций'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='volume_h1',
            field=models.FloatField(blank=True, null=True, verbose_name='Объём торгов (1 час)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='volume_h24',
            field=models.FloatField(blank=True, null=True, verbose_name='Объём торгов (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='volume_h6',
            field=models.FloatField(blank=True, null=True, verbose_name='Объём торгов (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='volume_m5',
            field=models.FloatField(blank=True, null=True, verbose_name='Объём торгов (5 минут)'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transfers_b',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество трансферов'),
        ),
    ]
