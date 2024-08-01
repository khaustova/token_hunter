import os
from datetime import datetime
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dexscreener import DexscreenerClient

# client = DexscreenerClient()
# files = os.listdir("./dex_parser/page_sources/coins")

# with open ("./dex_parser/page_sources/coins/coins_page-1.html", "r", encoding="utf-8") as file:
#     soup = BeautifulSoup(file.read(), "html.parser")
#     links = soup.find_all("a", class_="ds-dex-table-row ds-dex-table-row-top")
#     pairs_on_the_page = [a.get("href")[8:] for a in links]
    
#     temp_df = pd.DataFrame(
#         columns=[
#             "name",
#             "pair_address", 
#             "token_address",
#             "created_date",
#         ]
#     )
    
#     pair = "9djrgmvqhxejzerysc4lwcsaeaepxh1pcxuzljvnfv77"

#     data = client.search_pairs("9djrgmvqhxejzerysc4lwcsaeaepxh1pcxuzljvnfv77")[0]

#     temp_df.loc[len(temp_df.index )] = [
#         data.base_token.name,
#         data.pair_address,
#         data.base_token.address,
#         data.pair_created_at,
#     ]
#     temp_df.to_csv('output.csv')
    
with open ("./dex_parser/page_sources/top_traders/KNIGHT.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file.read(), "html.parser")
    links = soup.find_all("a", class_="chakra-link chakra-button custom-1hhf88o")
    makers = [a.get("href").split("/")[-1] for a in links]
    sums = soup.find_all("div", class_="custom-1o79wax")
    for i in range(len(sums)):
        if i % 2 == 0:
            bought = sums[i].find("span").text
        else:
            sold = sums[i].find("span").text
    name = soup.find("h2", class_="chakra-heading custom-to0qxc")
    token_address_link = soup.find_all("a", class_="chakra-link chakra-button custom-isf5h9")[1]
    token_addres = token_address_link.get("href").split("/")[-1]

    
        

    