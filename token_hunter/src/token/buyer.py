import logging
from telethon import TelegramClient

logger = logging.getLogger(__name__)


async def real_buy_token(token_address: str, telegram_client: TelegramClient) -> None:
    """Executes actual token purchase via Maestro bot.
    
    Args:
        token_address: Token contract address.
        telegram_client: Configured Telegram client instance.
    
    Raises:
        ConnectionError: If Telegram connection fails.
    """
    try:
        await telegram_client.connect()
        await telegram_client.send_message("@maestro", token_address)
        logger.info("Purchased token %s via Maestro Bot", token_address)
    except Exception as e:
        logger.error("Failed to purchase token %s: %s", token_address, str(e))
    finally:
        await telegram_client.disconnect()

