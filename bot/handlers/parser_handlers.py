from typing import Any
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dexscreener_parser.dex_parser import parse_coins

router = Router()

@router.message(Command(commands=['dex']))
async def start_command(message: Message):
    """
    Обработчик команды /start сохраняет информацию о новом пользователе и
    выводит инлайн-клавиатуру с меню выбора заданий.
    """
    await message.answer(
        text="Dex!!",
    )
    await parse_coins(1, filter="?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=10") 