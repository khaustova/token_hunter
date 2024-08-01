import time
from datetime import datetime
from seleniumbase import SB

def parse_coins(pages: int, filter: str=""):
    with SB(uc=True, test=True) as sb:
        for page in range(1, pages + 1):
            sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + str(page) + filter, reconnect_time=4)
            if page == 1:
                sb.uc_gui_handle_cf()
            sb.sleep(3)
            sourse = sb.get_page_source()
            date = datetime.now().strftime("%Y.%m.%d %H-%M")
            file_name = f"{date} coins_page-{str(page)}.html"
            sb.save_data_as(sourse, file_name, "./dex_parser/page_sources/coins")
            

def parse_top_traders(pairs: list[str]):
    with SB(uc=True, test=True) as sb:
        for pair in pairs:
            url = "https://dexscreener.com/solana/" + pair
        
            sb.uc_open_with_reconnect(url, reconnect_time=4)
            sb.uc_gui_handle_cf()
            time.sleep(3)
        
            sb.click('button:contains("Top Traders")')
            time.sleep(3)
        
            source = sb.get_page_source()
            title = sb.get_title()
            file_name = title.split()[0] + ".html"
            sb.save_data_as(source, file_name, "./dex_parser/page_sources/top_traders")
            
#parse_coins(2, filter="?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=10")
parse_top_traders(["14loyzvp42z3veeg1wldilbenmoecttooqcnhwddztnu"])


