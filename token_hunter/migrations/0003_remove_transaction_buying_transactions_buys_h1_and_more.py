# Generated by Django 5.1 on 2024-10-10 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_hunter', '0002_remove_toptrader_maker_toptrader_wallet_address_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='buying_transactions_buys_h1',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='buying_transactions_buys_m5',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='buying_transactions_sells_h1',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='buying_transactions_sells_m5',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='selling_transactions_buys_h1',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='selling_transactions_buys_m5',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='selling_transactions_sells_h1',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='selling_transactions_sells_m5',
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_buys_h1',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок на момент покупки (1 час)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_buys_h24',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок на момент покупки (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_buys_h6',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок на момент покупки (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_buys_m5',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок на момент покупки (5 минут)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_price_change_h24',
            field=models.FloatField(blank=True, null=True, verbose_name='Изменение цены на момент покупки (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_price_change_h6',
            field=models.FloatField(blank=True, null=True, verbose_name='Изменение цены на момент покупки (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_sells_h1',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж на момент покупки (1 час)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_sells_h24',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж на момент покупки (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_sells_h6',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж на момент покупки (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_sells_m5',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж на момент покупки (5 минут)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_volume_h24',
            field=models.FloatField(blank=True, null=True, verbose_name='Объём торгов на момент покупки (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='buying_volume_h6',
            field=models.FloatField(blank=True, null=True, verbose_name='Объём торгов на момент покупки (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_buys_h1',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок на момент продажи (1 час)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_buys_h24',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок на момент продажи (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_buys_h6',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок на момент продажи (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_buys_m5',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество покупок на момент продажи (5 минут)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_price_change_h24',
            field=models.FloatField(blank=True, null=True, verbose_name='Изменение цены на момент продажи (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_price_change_h6',
            field=models.FloatField(blank=True, null=True, verbose_name='Изменение цены на момент продажи (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_sells_h1',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж на момент продажи (1 час)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_sells_h24',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж на момент продажи (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_sells_h6',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж на момент продажи (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_sells_m5',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество продаж на момент продажи (5 минут)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_volume_h24',
            field=models.FloatField(blank=True, null=True, verbose_name='Объём торгов на момент продажи (24 часа)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='selling_volume_h6',
            field=models.FloatField(blank=True, null=True, verbose_name='Объём торгов на момент продажи (6 часов)'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N1',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 1-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N10',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 10-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N2',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 2-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N3',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 3-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N4',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 4-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N5',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 5-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N6',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 6-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N7',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 7-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N8',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 8-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_bought_N9',
            field=models.FloatField(blank=True, null=True, verbose_name='Покупка 9-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N1',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 1-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N10',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 10-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N2',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 2-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N3',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 3-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N4',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 4-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N5',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 5-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N6',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 6-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N7',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 7-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N8',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 8-го снайпера'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='snipers_sold_N9',
            field=models.FloatField(blank=True, null=True, verbose_name='Продажа 9-го снайпера'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='total_transactions_max',
            field=models.IntegerField(blank=True, null=True, verbose_name='Максимальное количество транзакций'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='total_transactions_min',
            field=models.IntegerField(blank=True, null=True, verbose_name='Минимальное количество транзакций'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='total_transfers_max',
            field=models.IntegerField(blank=True, null=True, verbose_name='Максимальное количество трансферов'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='total_transfers_min',
            field=models.IntegerField(blank=True, null=True, verbose_name='Минимальное количество трансферов'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='transactions_buys_h1_max',
            field=models.IntegerField(blank=True, null=True, verbose_name='Максимальное количество покупок (1 час)'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='transactions_buys_h1_min',
            field=models.IntegerField(blank=True, null=True, verbose_name='Минимальное количество покупок (1 час)'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='transactions_sells_h1_max',
            field=models.IntegerField(blank=True, null=True, verbose_name='Максимальное количество продаж (1 час)'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='transactions_sells_h1_min',
            field=models.IntegerField(blank=True, null=True, verbose_name='Минимальное количество продаж (1 час)'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='buying_total_transactions',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество транзакций на момент покупки'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='buying_total_transfers',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество трансферов на момент покупки'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_bought_1000_2500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, купившие на 1000$ - 2500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_bought_100_500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, купившие на 100$ - 500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_bought_100_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, купившие меньше, чем на 100$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_bought_2500_5000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, купившие на 2500$ - 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_bought_5000_more',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, купившие больше, чем на 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_bought_500_1000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, купившие на 500$ - 1000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_held_all',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, которые держат'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_no_bought',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы без покупки'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_pnl_1000_2500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы с PNL 1000$ - 2500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_pnl_100_500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы с PNL 100$ - 500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_pnl_100_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы с PNL меньше, чем 100$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_pnl_2500_5000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы с PNL 2500$ - 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_pnl_5000_more',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы с PNL больше, чем 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_pnl_500_1000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы с PNL 500$ - 1000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_pnl_loss',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы с отрицательным PNL'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_pnl_profit',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы с положительным PNL'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_sold_1000_2500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие на 1000$ - 2500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_sold_100_500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие на 100$ - 500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_sold_100_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие меньше, чем на 100$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_sold_2500_5000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие на 2500$ - 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_sold_5000_more',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие больше, чем на 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_sold_500_1000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие на 500$ - 1000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_sold_all',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие всё'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='snipers_sold_some',
            field=models.IntegerField(blank=True, null=True, verbose_name='Снайперы, продавшие часть'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_bought_1000_2500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, купившие на 1000$ - 2500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_bought_100_500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, купившие на 100$ - 500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_bought_100_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, купившие меньше, чем на 100$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_bought_2500_5000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, купившие на 2500$ - 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_bought_5000_more',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, купившие больше, чем на 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_bought_500_1000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, купившие на 500$ - 1000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_no_bought',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы без покупки'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_no_sold',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы без продажи'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_pnl_1000_2500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы с PNL 1000$ - 2500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_pnl_100_500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы с PNL 100$ - 500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_pnl_100_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы с PNL меньше, чем на 100$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_pnl_2500_5000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы с PNL 2500$ - 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_pnl_5000_more',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы с PNL больше, чем 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_pnl_500_1000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы с PNL 500$ - 1000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_pnl_loss',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы с отрицательным PNL'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_pnl_profit',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы с положительным PNL'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_sold_1000_2500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, продавшие на 1000$ - 2500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_sold_100_500',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, продавшие на 100$ - 500$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_sold_100_less',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, продавшие меньше, чем на 100$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_sold_2500_5000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, продавшие на 2500$ - 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_sold_5000_more',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, продавшие больше, чем на 5000$'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='top_traders_sold_500_1000',
            field=models.IntegerField(blank=True, null=True, verbose_name='Топы, продавшие на 500$ - 1000$'),
        ),
    ]
