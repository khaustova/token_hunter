import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from telethon.sync import TelegramClient
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from telethon.errors import SessionPasswordNeededError

     
async def telegram_authorize():
    """Authorizes Telegram client by entering login code.
    
    Handles the complete authorization flow including:
    - Creating/updating app credentials in database.
    - Managing client sessions.
    - Processing login code or password when required.
    """
    app, _ = App.objects.update_or_create(
    api_id=settings.TELETHON_API_ID,
    api_hash=settings.TELETHON_API_HASH
    )
    cs, _ = ClientSession.objects.update_or_create(
        name="default",
    )
    telegram_client = TelegramClient(DjangoSession(client_session=cs), app.api_id, app.api_hash)
    await telegram_client.connect()
    
    if not await telegram_client.is_user_authorized():
        phone = settings.TELEGRAM_PHONE_NUMBER
        await telegram_client.send_code_request(phone)
        code = input("Enter verification code: ")
        try:
            await telegram_client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input("Enter password: ")
            await telegram_client.sign_in(password=password)
  
          
class Command(BaseCommand):
    """Django management command for Telegram authentication."""
    
    def handle(self, *args, **kwargs):
        help = "Telegram authorization for sending contract addresses to Maestro bot."
        
        asyncio.run(telegram_authorize())