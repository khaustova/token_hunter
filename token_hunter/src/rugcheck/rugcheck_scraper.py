import time
import logging
from nodriver.core.browser import Browser
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

logger = logging.getLogger(__name__)


async def scrape_rugcheck_with_nodriver(browser: Browser, token_address: str) -> dict:
    """Проверяет токен по адресу на сайте rugcheck.xyz.
    
    Notes:
        Использует уже открытый браузер для открытия сайта.

    Args:
        browser: Экземпляр браузера Chrome.
        token_address: Адрес токена.

    Returns:
        Словарь с результатами проверки токена.
    """
    url = "https://rugcheck.xyz/tokens/" + token_address
    rugcheck_page = await browser.get(url, new_tab=True)
    await rugcheck_page

    time.sleep(5)

    try:
        risk_level_element = await rugcheck_page.query_selector("div.risk h1.mb-0")
        risk_level = risk_level_element.text
    except Exception:
        risk_level = None

    try:
        mutable_metadata = await rugcheck_page.find("Mutable metadata")
        is_mutable_metadata = True
    except Exception:
        is_mutable_metadata = False

    result = {
        "risk_level": risk_level,
        "is_mutable_metadata": is_mutable_metadata,
    }

    logger.debug(f"Уровень риска токена {token_address}: {risk_level}")

    await rugcheck_page.close()

    return result


def scrape_rugcheck_with_selenium(driver: WebDriver, token_address: str) -> dict:
    """Проверяет токен по адресу на сайте rugcheck.xyz.

    Использует уже созданный экземпляр веб-драйвера Selenium для открытия сайта.

    Args:
        driver: Экземпляр веб-драйвера.
        token_address: Адрес токена.

    Returns:
        Словарь с результатами проверки токена.
    """
    url = "https://rugcheck.xyz/tokens/" + token_address
    driver.get(url)

    time.sleep(5)

    risk_level = None 
    try:
        risk_level = driver.find_element(By.XPATH, "//div[contains(@class, 'risk')]/h1").text
    except Exception:
        pass

    is_mutable_metadata = False

    try:
        mutable_metadata = driver.find_element(By.XPATH, "//*[text()='Mutable metadata']")
        is_mutable_metadata = True
    except Exception:
        is_mutable_metadata = False

    result = {
        "risk_level": risk_level,
        "is_mutable_metadata": is_mutable_metadata,
    }

    logger.debug(f"Уровень риска токена {token_address}: {risk_level}")

    return result
