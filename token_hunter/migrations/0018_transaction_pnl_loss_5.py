# Generated by Django 5.1 on 2025-01-17 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_hunter', '0017_transaction_pnl_loss_10'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='PNL_loss_5',
            field=models.BooleanField(blank=True, null=True, verbose_name='PNL -10 %'),
        ),
    ]
