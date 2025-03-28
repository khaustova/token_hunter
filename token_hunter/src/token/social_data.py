import time
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from nodriver.core.browser import Browser
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest

from token_hunter.src.utils.preprocessing_data import clear_number

logger = logging.getLogger(__name__)


async def get_social_info(
    browser: Browser | None,
    social_data: dict,
    telegram_client: TelegramClient
) -> dict:
    """Собирает и возвращает данные о социальных сетях токена (Twitter и Telegram).

    Note:
        Для Twitter данные собираются через getmoni.io
        Для Telegram используется Telegram API и Telethon.
        
    Args:
        browser: Экземпляр браузера Chrome для сбора данных Twitter.
        social_data: Словарь с данными по социальным сетям токена.
        telegram_client: Созданный и настроенный Telegram-client.

    Returns:
        dict: Словарь с данными по Twitter и Telegram.
    """
    twitter_data, telegram_data = None, None
    if social_data:
        for data in social_data:
            if data.get("type") == "twitter":
                twitter_name = data.get("url").split("/")[-1]
                # Проблемы с доступок к getmoni с Билайна, поэтому пока Твиттер не :(
                # twitter_data = await get_twitter_data(browser, twitter_name)
            elif data.get("type") == "telegram":
                channel_name = data.get("url").split("/")[-1]
                telegram_data = await get_telegram_data(telegram_client, channel_name)

    return {
        "twitter_data": twitter_data,
        "telegram_data": telegram_data
    }


async def get_twitter_data(browser: Browser, twitter_name: str) -> dict:
    """Получает данные о Twitter-аккаунте токена с getmoni.io.

    Args:
        browser: Экземпляр браузера Chrome для взаимодействия с getmoni.io.
        twitter_name: Имя в Twitter (без @).
        
    Note: 
        Собирает следующие данные:
            twitter_followers (int): Общее количество подписчиков.
            twitter_smart_followers (int): Количество инфлюенсеров.
            twitter_days (int): Возраст аккаунта в днях.
            twitter_tweets (int): Количество твитов.
            is_twitter_error (bool): Флаг ошибки получения данных.  

    Returns:
        Словарь с данными о Twitter-аккаунте токена.
    """

    getmoni_page = await browser.get(
        "https://discover.getmoni.io/" + twitter_name, 
        new_tab=True
    )
    await getmoni_page

    time.sleep(8)
    twitter_data = {}

    try:
        not_found = await getmoni_page.find("Not found")
    except Exception:
        not_found = False

    if not_found:
        twitter_data["is_twitter_error"] = True
        return twitter_data

    try:
        page_src = await getmoni_page.query_selector(
            "main > div > div"
        )
        await page_src
        page_html = await page_src.get_html()
        soup = BeautifulSoup(page_html, "html.parser")

        followers_element = (
            soup
            .find("div")
            .find_all("section")[1]
            .find_all("article")[0]
            .find("div")
            .find_all("div")[1]
        )
        twitter_data["twitter_followers"] = (
            followers_element
            .find_all("div")[3]
            .find_all("span")[0]
            .text
        )
        twitter_data["twitter_followers"] = clear_number(twitter_data["twitter_followers"])
        twitter_data["twitter_smart_followers"] = (
            followers_element
            .find_all("div")[6]
            .find_all("span")[1]
            .text
        )
        twitter_data["twitter_smart_followers"] = clear_number(twitter_data["twitter_smart_followers"])
        twitter_data["is_twitter_error"] = False

        info_element = (
            soup
            .find("div")
            .find_all("div", recursive=False)[0]
            .find_all("article")[1]
        )
        created_date_str = (
            info_element
            .find_all("li")[1]
            .find_all("span")[1]
            .text
        )
        created_date = datetime.strptime(created_date_str, "%d %b %Y").date()
        twitter_data["twitter_days"] = (datetime.now().date() - created_date).days
        twitter_data["twitter_tweets"] = (
            info_element
            .find_all("li")[-1]
            .find_all("span")[1]
            .text
        )
        if twitter_data["twitter_tweets"] == "—":
            twitter_data["twitter_tweets"] = 0
        else:
            try:
                twitter_data["twitter_tweets"] = clear_number(twitter_data["twitter_tweets"])
            except Exception:
                twitter_data["twitter_tweets"] = -1

    except Exception:
        pass

    await getmoni_page.close()

    return twitter_data


async def get_telegram_data(telegram_client: TelegramClient, raw_channel_name: str) -> dict:
    """Получает данные о Telegram-канале токена через Telegram API.

    Args:
        telegram_client: Созданный и настроенный Telegram-client.
        raw_channel_name (str): Необработанное имя Telegram-канала.
        
    Note: 
        Собирает следующие данные:
            telegram_members (int | None): Количество участников
            is_telegram_error (bool): Флаг ошибки получения данных

    Returns:
        Словарь с данными о Telegram-канале токена.
    """

    channel_name = ""
    for letter in raw_channel_name:
        if letter.isalnum() or letter == "_":
            channel_name += letter
        else:
            break

    telegram_data = {}

    await telegram_client.connect()

    try:
        channel_connect = await telegram_client.get_entity(channel_name)
        channel_full_info = await telegram_client(GetFullChannelRequest(channel=channel_connect))
        telegram_data["telegram_members"] = int(channel_full_info.full_chat.participants_count)
        telegram_data["is_telegram_error"] = False
    except Exception:
        telegram_data["is_telegram_error"] = True

    await telegram_client.disconnect()

    return telegram_data
