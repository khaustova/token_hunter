import time
import logging
from nodriver.core.browser import Browser

logger = logging.getLogger(__name__)


async def get_total_transfers(browser: Browser, token_address: str) -> int | None:
    """
    Возвращает количество трансферов токена token_address с solscan.io.
    """
    
    url = "https://solscan.io/token/" + token_address
    solcan_page = await browser.get(url, new_tab=True)
    await solcan_page
    
    time.sleep(7)

    total_transfers = None 
    try:
        total_transfers_div = await solcan_page.find("transfer(s)")
        total_transfers_list = total_transfers_div.text_all.split()
        if total_transfers_list[0] == "More":
            total_transfers = total_transfers_list[2].replace(",", "")
        elif total_transfers_list[0] == "Total":
            total_transfers = total_transfers_list[1].replace(",", "")
    except:
        pass
        
    await solcan_page.close()

    return int(total_transfers) if total_transfers else None