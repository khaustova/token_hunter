import time
import logging
import pandas as pd
import random
from seleniumbase import SB
from bs4 import BeautifulSoup
from dexscreener import DexscreenerClient
from toss_a_coin.models import TopTrader
from ..models import TopTrader
from django.contrib.admin.models import LogEntry, ADDITION

logger = logging.getLogger(__name__)


class DexScreenerParser():
    
    def __init__(self, sb: SB):
        self.sb = sb
        self.client = DexscreenerClient()
                     
    def parse_top_traders_from_the_pages(self, pages: int, filter: str=""):
        for page in range(1, pages + 1):
            logger.info(f"Открытие страницы {page}")
            self.sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + str(page) + filter, reconnect_time=4)
            if page == 1:
                self.sb.uc_gui_handle_cf()
            self.sb.sleep(random.randint(6, 7))
            
            if self.sb.get_title() == "Just a moment...":
                logger.error("Не удалось победить Cloudflare")
                raise Exception("Cloudflare! :(")
            
            logger.info(f"Начата загрузка информации по монетам на странице {page}")     
            links = self.sb.find_elements("//a[contains(@class, 'ds-dex-table-row')]", by="xpath")

            for link in links:
                try:
                    link_href = link.get_attribute("href")
                    pair = link_href.split("/")[-1]
                    if TopTrader.objects.filter(pair=pair):
                        logger.debug(f"Монета на странице {link.get_attribute("href")} уже проанализирована")
                        continue
                    else:
                        link.click()
                except Exception as e:
                    logger.error(f"Не удалось прочитать адрес ссылки")
                    continue

                self.sb.sleep(random.randint(2, 3))
                
                try:
                    self.sb.find_element("//span[text()='No issues']", by="xpath")
                except Exception as e:
                    logger.info(f"Монета на странице {link.get_attribute("href")} небезопасна")
                    token_address_link = soup.find_all("a", class_="chakra-link chakra-button custom-isf5h9")[1]
                    token_addres = token_address_link.get("href").split("/")[-1]
                    self.sb.go_back()
                    time.sleep(random.randint(2, 3))
                    continue
                
                try:
                    self.sb.click('button:contains("Top Traders")') 
                    time.sleep(random.randint(2, 3))
                    page_sourse = self.sb.get_page_source()
                    soup = BeautifulSoup(page_sourse, "html.parser")
                    self.save_top_traders(pair, soup)
                except Exception as e:
                    logger.error(f"Не удалось открыть вкладку с топовыми кошельками на странице {link.get_attribute("href")}")
                
                self.sb.go_back()
                time.sleep(random.randint(2, 3))
            
    def save_top_traders(self, pair, soup):
        token_address_link = soup.find_all("a", class_="chakra-link chakra-button custom-isf5h9")[1]
        token_addres = token_address_link.get("href").split("/")[-1]
        
        links = soup.find_all("a", class_="chakra-link chakra-button custom-1hhf88o")
        data = {}

        data["makers"] = [a.get("href").split("/")[-1] for a in links]
        
        sums = soup.find_all("div", class_="custom-1o79wax")
        bought_list = []
        sold_list = []
        for i in range(len(sums)):
            if sums[i].find("span").text == "-":
                number = None
            else:
                number = self._covert_str_number_to_int(sums[i].find("span").text[1:])
            
            if i % 2 == 0:
                bought_list.append(number)
            else:
                sold_list.append(number)
        data["bought"] = bought_list
        data["sold"] = sold_list

        token_address_link = soup.find_all("a", class_="chakra-link chakra-button custom-isf5h9")[1]
        token_addres = token_address_link.get("href").split("/")[-1]
        chain = "SOL"
        
        temp_df = pd.DataFrame(data)
        temp_df.dropna(inplace=True)
        temp_df["pnl"] = temp_df["sold"] - temp_df["bought"]
        
        for index, row in temp_df.iterrows():
            tt = TopTrader.objects.create(
                coin=token_addres,
                pair = pair,
                maker=row["makers"],
                chain=chain,
                bought=row["bought"],
                sold=row["sold"],
                PNL=row["pnl"]    
            )
        logger.debug(f"Успешно загружена информация по монете {token_addres}")
        
        # LogEntry.objects.log_action(
        #     user_id=1, 
        #     content_type_id=TopTrader.objects.get_for_model(tt).pk,
        #     object_id=tt.pk,
        #     object_repr=str(tt),
        #     action_flag=ADDITION,
        #     change_message="Описание изменений"
        # )
        
    def _covert_str_number_to_int(self, str_number: str) -> int:
        number = str_number.lstrip("0").lstrip("$")
        number = number.replace(",", "").replace(".", "").replace("K", "000").replace("M", "000000")
        number = int(number)
        
        return number
    
