from typing import Any
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

router = Router()

@router.message(Command(commands=['start']))
async def start_command(message: Message):
    """
    Обработчик команды /start сохраняет информацию о новом пользователе и
    выводит инлайн-клавиатуру с меню выбора заданий.
    """
    await message.answer(
        text="Hi!",
    )