# Generated by Django 5.1 on 2024-08-16 21:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0003_rename_network_toptrader_chain'),
    ]

    operations = [
        migrations.AddField(
            model_name='toptrader',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
