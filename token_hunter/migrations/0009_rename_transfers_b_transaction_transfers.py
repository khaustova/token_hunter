# Generated by Django 5.1 on 2024-11-18 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('token_hunter', '0008_remove_transaction_buys_h1_b_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='transfers_b',
            new_name='transfers',
        ),
    ]
