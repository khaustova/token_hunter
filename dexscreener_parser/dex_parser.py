import time
import asyncio
from datetime import datetime
from seleniumbase import SB
from bs4 import BeautifulSoup
import pandas as pd
from handlers import save_coins, save_top_traders


async def parse_coins(pages: int, filter: str=""):
    with SB(uc=True, test=True) as sb:
        for page in range(1, pages + 1):
            sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + str(page) + filter, reconnect_time=4)
            if page == 1:
                sb.uc_gui_handle_cf()
            sb.sleep(3)
            page_sourse = sb.get_page_source()
            await save_coins(page_sourse)
            # date = datetime.now().strftime("%Y.%m.%d %H-%M")
            # file_name = f"{date} coins_page-{str(page)}.html"
            # sb.save_data_as(sourse, file_name, "./dex_parser/page_sources/coins")
            
def parse_top_traders(pairs: list[str]=None):
    with SB(uc=True, test=True) as sb:
        for pair in pairs:
            url = "https://dexscreener.com/solana/" + pair
        
            sb.uc_open_with_reconnect(url, reconnect_time=4)
            sb.uc_gui_handle_cf()
            time.sleep(3)
        
            sb.click('button:contains("Top Traders")')
            time.sleep(3)
        
            page_source = sb.get_page_source()
            save_top_traders(page_source)
            # title = sb.get_title()
            # file_name = title.split()[0] + ".html"
            # sb.save_data_as(source, file_name, "./dex_parser/page_sources/top_traders")
            
def parse_top_traders_from_the_page(pages: int, filter: str=""):
    with SB(uc=True, test=True) as sb:
        for page in range(1, pages + 1):
            sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + str(page) + filter, reconnect_time=4)
            if page == 1:
                sb.uc_gui_handle_cf()
            sb.sleep(3)
            page_sourse = sb.get_page_source()

            # date = datetime.now().strftime("%Y.%m.%d %H-%M")
            # file_name = f"{date} coins_page-{str(page)}.html"
            # sb.save_data_as(sourse, file_name, "./dex_parser/page_sources/coins")
            
            

async def main():
    address = "5Mbqo6CWrXSXuaJnd1s699oqB4upGP7oenVDQjzeLGvv"
    oldest_signature = await parse_coins(1, filter="?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=10")  

if __name__ == "__main__":
    asyncio.run(main())          

# if __name__ == "__main__":       
#     parse_coins(1, filter="?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=10")
    #parse_top_traders(["299XwCopfifHHoE4UsBC2SrAa63dzppk8gv7rh3CpG9C"])


