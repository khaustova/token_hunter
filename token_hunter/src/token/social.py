import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from ..utils.preprocessing_data import clear_number
logger = logging.getLogger(__name__)


async def get_social_info(social_data: dict) -> tuple:
    """
    Возвращает данные о телеграме и твиттере токена.
    """
    
    twitter_data, telegram_data = None, None
    if social_data:
        for data in social_data:
            if data.get("type") == "twitter":
                twitter_name = data.get("url").split("/")[-1]
                twitter_data = await get_twitter_data(twitter_name)
            elif data.get("type") == "telegram":
                channel_name = data.get("url").split("/")[-1]
                telegram_data = await get_telegram_data(channel_name)
                    
    return (twitter_data, telegram_data)


async def get_twitter_data(browser, twitter_name: str) -> dict:
    """
    Получает данные о твиттере токена: количестве подписчиков, 
    в т.ч. известных, возрасте аккаунта и количестве твитов,  
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
    except:
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
            except:
                twitter_data["twitter_tweets"] = -1
        
    except:
        pass
    
    await getmoni_page.close()

    return twitter_data    


async def get_telegram_data(telegram_client: TelegramClient, raw_channel_name: str) -> dict:
    """
    Получает данные о телеграм-канале токена: количестве подписчиков, 
    возрасте первого чата и наличии отметки 'скам'.
    """
    
    channel_name = ""
    for letter in raw_channel_name:
        if letter.isalnum() or letter == "_":
            channel_name += letter;
        else:
            break

    telegram_data = {}
    
    await telegram_client.connect()
    
    try:       
        channel_connect = await telegram_client.get_entity(channel_name)
        channel_full_info = await telegram_client(GetFullChannelRequest(channel=channel_connect))
        telegram_data["telegram_members"] = int(channel_full_info.full_chat.participants_count)
        telegram_data["is_telegram_error"] = False
    except:
        telegram_data["is_telegram_error"] = True
    
    await telegram_client.disconnect()
    
    return telegram_data
