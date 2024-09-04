import time
from smtplib import SMTPException
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.utils.html import escape
from django.utils.safestring import SafeText
from django.template.loader import get_template
from seleniumbase import SB
from time import sleep
from random import randint
from celery import shared_task
from .dexscreener_worker import DexScreeneWatcher
from celery import shared_task
from core.celery import app
import random
from celery.contrib.abortable import AbortableTask

@app.task(bind=True, base=AbortableTask)
def watch_dexscreener_task(self, filter: str) -> str:
    with SB(
        uc=True, 
        test=True, 
        #headless2=True,
        extension_dir=settings.CAPTCHA_EXTENSION_DIR
    ) as sb:
        dex_parser = DexScreeneWatcher(sb)
        dex_parser.watch_coins(filter)
    
    return f"Анализ dexscreener"