import time
import pandas as pd
from datetime import datetime
from seleniumbase import SB
from bs4 import BeautifulSoup
from dexscreener import DexscreenerClient
from parser.models import TopTrader

class DexScreenerParser():
    
    def __init__(self, sb: SB):
        self.sb = sb
        self.client = DexscreenerClient()
    
    def parse_coins(self, pages: int=1, filter: str=""):
        for page in range(1, pages + 1):
            self.sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + str(page) + filter, reconnect_time=10)
            if page == 1:
                self.sb.uc_gui_handle_cf()
            self.sb.sleep(3)
            page_sourse = self.sb.get_page_source()
            self.save_coins(page_sourse)
            
    def save_coins(self, page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        links = soup.find_all("a", class_="ds-dex-table-row ds-dex-table-row-top")
        pairs_on_the_page = [a.get("href")[8:] for a in links]
        
        temp_df = pd.DataFrame(
            columns=[
                "name",
                "pair_address", 
                "token_address",
                "created_date",
            ]
        )
        
        token_name, pair_addres, token_address, created_at = [], [], [], []   

        for pair in pairs_on_the_page:
            data = self.client.search_pairs(pair)
            
            for token in data: 
                token_name.append(token.base_token.name)
                pair_addres.append(token.pair_address)
                token_address.append(token.base_token.address)
                created_at.append(token.pair_created_at)

        temp_df = pd.DataFrame(
            {
                "name": token_name, 
                "pair_address": pair_addres,
                "token_address": token_address,
                "created_at": created_at
            }
        )
        temp_df.to_csv('output_coin.csv')
                
    def parse_top_traders(self, pair: str):
        url = "https://dexscreener.com/solana/" + pair
    
        self.sb.uc_open_with_reconnect(url, reconnect_time=4)
        self.sb.uc_gui_handle_cf()
        time.sleep(3)
    
        self.sb.click('button:contains("Top Traders")')
        time.sleep(3)
    
        page_source = self.sb.get_page_source()
        self.save_top_traders(page_source)
                        
    def parse_top_traders_from_the_pages(self, pages: int, filter: str="", is_top_traders: bool=True, is_top_snipers: bool=False):
        for page in range(1, pages + 1):
            self.sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + str(page) + filter, reconnect_time=4)
            if page == 1:
                self.sb.uc_gui_handle_cf()
            self.sb.sleep(6)
            
            links = self.sb.find_elements("//a[contains(@class, 'ds-dex-table-row')]", by="xpath")
            for link in links:
                link.click()
                
                self.sb.sleep(2)
                try:
                    self.sb.find_element("//span[text()='No issues']", by="xpath")
                except:
                    self.sb.go_back()
                    time.sleep(2)
                    continue
                
                if is_top_traders:
                    self.sb.click('button:contains("Top Traders")')
                    time.sleep(3)
                    
                    page_sourse = self.sb.get_page_source()
                    self.save_top_traders(page_sourse)
                    
                    self.sb.go_back()
                    time.sleep(2)
            
    def save_top_traders(self, page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        
        token_address_link = soup.find_all("a", class_="chakra-link chakra-button custom-isf5h9")[1]
        token_addres = token_address_link.get("href").split("/")[-1]
        
        if TopTrader.objects.filter(coin=token_addres):
            return None
        
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
                number = self.covert_str_number_to_int(sums[i].find("span").text[1:])
            
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
        
        for index, row in temp_df.iterrows():
            TopTrader.objects.create(
                coin=token_addres,
                maker=row["makers"],
                chain=chain,
                bought=row["bought"],
                sold=row["sold"],
                PNL=((row["sold"] - row["bought"]) / row["bought"] * 100)      
            )
        
        temp_df.to_csv('output_top.csv')
        
    def covert_str_number_to_int(self, str_number: str):
        number = str_number.replace(",", "").replace(".", "").replace("K", "000").replace("M", "000000")
        number = int(number)
        return number
