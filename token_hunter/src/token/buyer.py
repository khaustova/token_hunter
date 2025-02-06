import logging
from telethon import TelegramClient

logger = logging.getLogger(__name__)


async def real_buy_token(token_address: str, telegram_client: TelegramClient,) -> None:
    """
    Реальная покупка токена через бот Maestro
    """  
    
    await telegram_client.connect()

    await telegram_client.send_message("@maestro", token_address)
    
    await telegram_client.disconnect()

    logger.info(f"Покупка токена {token_address} через Maestro Bot")
