import logging
from .loader import bot, dp
from .keyboards.commands_menu import set_commands_menu
from .handlers import menu_handlers, parser_handlers


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        #filename='logs/bot.log',filemode='w',
        format='%(asctime)s: %(levelname)s - %(name)s - %(message)s',
    )
    
    
    dp.include_routers(
        menu_handlers.router,
        parser_handlers.router
    )
    
    await set_commands_menu(bot)
    
    await dp.start_polling(bot)