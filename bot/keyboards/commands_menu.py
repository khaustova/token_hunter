from aiogram import Bot
from aiogram.types import BotCommand


COMMANDS: dict[str, str] = {
    '/menu': 'Меню выбора заданий',
    '/dex': 'Dex',
}


async def set_commands_menu(bot: Bot):
    commands_menu = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in COMMANDS.items()
    ]
    await bot.set_my_commands(commands_menu)