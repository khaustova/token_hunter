import asyncio
from django.core.management.base import BaseCommand
from bot.main import main


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        help = 'Starts a bot.'
                  
        asyncio.run(main())