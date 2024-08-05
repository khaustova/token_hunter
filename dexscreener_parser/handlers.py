import os
from datetime import datetime
import json
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dexscreener import DexscreenerClient

client = DexscreenerClient()

async def save_coins(page_source):
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
        data = await client.search_pairs_async(pair)
        
        for token in data: 
            token_name.append(token.base_token.name)
            pair_addres.append(token.pair_address)
            token_address.append(token.base_token.address)
            created_at.append(token.pair_created_at)
         
 
        # token_name.append(data.base_token.name)
        # pair_addres.append(data.pair_address)
        # token_address.append(data.base_token.address)
        # created_at.append(data.pair_created_at)

    temp_df = pd.DataFrame(
        {
            "name": token_name, 
            "pair_address": pair_addres,
            "token_address": token_address,
            "created_at": created_at
        }
    )
    temp_df.to_csv('output_coin.csv')

def save_top_traders(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    links = soup.find_all("a", class_="chakra-link chakra-button custom-1hhf88o")
    data = {}

    data["makers"] = [a.get("href").split("/")[-1] for a in links]

    sums = soup.find_all("div", class_="custom-1o79wax")
    bought_list = []
    sold_list = []
    for i in range(len(sums)):
        if i % 2 == 0:
            bought_list.append(sums[i].find("span").text)
        else:
            sold_list.append(sums[i].find("span").text)
    data["bought"] = bought_list
    data["sold"] = sold_list

    name = soup.find("h2", class_="chakra-heading custom-to0qxc")
    token_address_link = soup.find_all("a", class_="chakra-link chakra-button custom-isf5h9")[1]
    token_addres = token_address_link.get("href").split("/")[-1]
    
    temp_df = pd.DataFrame(data)
    temp_df.to_csv('output_top.csv')
  
    

    
    
    
        

    