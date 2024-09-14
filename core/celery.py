from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.enable_utc = False

app.conf.update(timezone="Europe/Moscow")

app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'every': { 
#         'task': 'toss_a_coin.sample_task',
#         'schedule': 2.0,# по умолчанию выполняет каждую минуту, очень гибко 
#     },                                                              # настраивается

# }