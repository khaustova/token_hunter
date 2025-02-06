import time
import logging
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


async def rugcheck(browser, token_address):
    """
    Возвращает уровень риска токена token_address с rugcheck.xyz. 
    Использует nodriver.
    """
    
    url = "https://rugcheck.xyz/tokens/" + token_address
    rugcheck_page = await browser.get(url, new_tab=True)
    await rugcheck_page
    
    time.sleep(5)
    
    risk_level = None 
    try:
        risk_level_element = await rugcheck_page.query_selector("div.risk h1.mb-0")
        risk_level = risk_level_element.text
    except:
        pass
    
    try:
        mutable_metadata = await rugcheck_page.find("Mutable metadata")
        is_mutable_metadata = True
    except:
        is_mutable_metadata = False
        
    result = {
        "risk_level": risk_level,
        "is_mutable_metadata": is_mutable_metadata,
    }
        
    await rugcheck_page.close()
    
    return result


def sync_rugcheck(driver, token_address):
    """
    Возвращает уровень риска токена token_address с rugcheck.xyz. 
    Использует Selenium.
    """
    
    url = "https://rugcheck.xyz/tokens/" + token_address
    driver.get(url)
    
    time.sleep(5)
    
    risk_level = None 
    try:
        risk_level_element = driver.find_element("div.risk h1.mb-0")
        risk_level = risk_level_element.text
    except:
        pass
    
    try:
        mutable_metadata = driver.find_element("Mutable metadata")
        is_mutable_metadata = True
    except:
        is_mutable_metadata = False
        
    result = {
        "risk_level": risk_level,
        "is_mutable_metadata": is_mutable_metadata,
    }
        
    driver.close()
    
    return result