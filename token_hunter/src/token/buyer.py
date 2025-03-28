import logging
from telethon import TelegramClient

logger = logging.getLogger(__name__)


async def real_buy_token(token_address: str, telegram_client: TelegramClient) -> None:
    """Покупает токен по адресу через бот Maestro.
    
    Args:
        token_address: Адрес контракта токена.
        telegram_client: Созданный и настроенный Telegram-client.
    
    """
    await telegram_client.connect()

    await telegram_client.send_message("@maestro", token_address)

    await telegram_client.disconnect()

    logger.info("Покупка токена %s через Maestro Bot", token_address)
