import time
import logging
from datetime import datetime
from urllib.parse import urljoin

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from logger import get_logger


logger = get_logger(__name__)


class SolscanParser:
    """
    Парсит данные с https://solscan.io/.
    """
    
    def __init__(self):
        self.url = "https://solscan.io/account/"
        self.driver = None

    def __enter__(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--headless")

        self.driver = uc.Chrome(use_subprocess=True, options=chrome_options)

        return self

    def __exit__(self, exc_type, exc_value, _):
        if exc_type:
            logger.error(f"При закрытии браузера произошла ошибка: {exc_value}")

        if self.driver:
            self.driver.close()

        return False
    
    def prepare_parsing(self, address: str):
        url = urljoin(self.url, address)

        driver = self.driver
        driver.get(url)

        driver.execute_script(f"window.open('{url}', '_blank')")
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)
        driver.close()
        
        driver.switch_to.window(driver.window_handles[0])
        
        return driver
        
    def get_balance(self, address: str):       
        driver = self.prepare_parsing(address)

        try:
            print(driver.title)
            logger.info(f"Начата загрузка баланса токенов на аккаунте {address}")
            
            balance_button = driver.find_element(By.XPATH, '//button[text()="Portfolio"]')
            balance_button.click()
            print(balance_button.text)
        
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        (
                            "//table/tbody/tr[2]/td[1]/span/span[1]/a"
                        ),
                    )
                )
            )
            return element.text
            
        except TimeoutException:
            logger.info(f"На странице не найдена информация по балансу на аккаунте {address}")
            pass

        return None

log_level: str = "INFO"
logging.basicConfig(level=log_level)

def main():
    address = "45ruCyfdRkWpRNGEqWzjCiXRHkZs8WXCLQ67Pnpye7Hp"
    with SolscanParser() as parser:
        result = parser.get_balance(address)
        print(result)


if __name__ == "__main__":
    main()