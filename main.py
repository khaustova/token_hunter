import asyncio
import logging
from parser.solana_parser.solana_parser import SolanaParser
from logger import get_logger
import time
import asyncio
from solana.rpc.api import Client
from typing import Optional
from helius import TransactionsAPI
from solders.signature import Signature
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp
from bot.configuration import configuration
from logger import get_logger
from bot.loader import bot, dp
from bot.keyboards.commands_menu import set_commands_menu
from bot.handlers import menu_handlers, parser_handlers
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis
from bot.configuration import configuration

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com/" 
SOLANA_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"

logger = get_logger(__name__)

log_level: str = "DEBUG"
logging.basicConfig(level=log_level)

async def main():
    
    dp.include_routers(
        menu_handlers.router,
        parser_handlers.router,
    )
    
    await set_commands_menu(bot)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())