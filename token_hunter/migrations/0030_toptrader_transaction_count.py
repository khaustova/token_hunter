# Generated by Django 5.1 on 2025-02-09 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_hunter', '0029_remove_settings_filter'),
    ]

    operations = [
        migrations.AddField(
            model_name='toptrader',
            name='transaction_count',
            field=models.IntegerField(default=0),
        ),
    ]
