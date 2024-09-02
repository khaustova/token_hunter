import logging
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class RugCheckParser:
    """
    Парсит проверку токена с https://rugcheck.xyz/.
    """
    
    def __init__(self, address: str):
        self.url = "https://rugcheck.xyz/tokens/"
        self.address = address
        self.driver = None

    def __enter__(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--headless")

        self.driver = uc.Chrome(
            use_subprocess=True, 
            options=chrome_options,
        )
        self.prepare_parsing()

        return self

    def __exit__(self, exc_type, exc_value, _):
        if exc_type:
            logger.error(f"При закрытии браузера произошла ошибка: {exc_value}")

        if self.driver:
            self.driver.close()

        return False
    
    def prepare_parsing(self) -> uc.Chrome:
        url = urljoin(self.url, self.address)

        driver = self.driver
        driver.get(url)

        driver.execute_script(f"window.open('{url}', '_blank')")
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)
        driver.close()
        
        driver.switch_to.window(driver.window_handles[0])
        
        return driver
        
    def get_risk_analysis(self) -> str:  
        try:
            risk_element = self.driver.find_element(
                By.XPATH, 
                "//*[@id='token-show']/div/div[3]/div[1]/div/div[2]/div/div[1]/h1"
            )
            
            return risk_element.text
            
        except TimeoutException:
            logger.error(f"На странице не найдена информация риску монеты {self.address}")
            
            return None
        
    def get_top_holders(self):
        try:
            rows = len(self.driver.find_elements(
                By.XPATH, 
                "//*[@id='token-show']/div/div[4]/div[2]/div/div[2]/table/tbody/tr"
                )
            )
            
            top_holders = {}
            for i in range(1, rows + 1):
                percentage_element = self.driver.find_element(
                    By.XPATH, 
                    f"//*[@id='token-show']/div/div[4]/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]"
                )
                percentage = float(percentage_element.text.strip("%"))
                
                account_element = self.driver.find_element(
                    By.XPATH, 
                    f"//*[@id='token-show']/div/div[4]/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/a"
                )
                account = account_element.get_attribute("href").split("/")[-1]
                
                if percentage >= 20 and account != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                    break
                
                top_holders[account] = percentage
                logger.debug(f"Топ держателей монеты {self.address}: {top_holders}")
            
        except TimeoutException:
            logger.error(f"На странице не найдена информация по тому держателей монеты {self.address}")
            
            return None
           
    def get_creator(self):
        try:
            creator_element = self.driver.find_element(
                By.XPATH,
                "//*[@id='token-show']/div/div[3]/div[2]/div/div[2]/table/tbody/tr[1]/td[3]/a"
            )
            creator = creator_element.get_attribute("href").split("/")[-1]
            logger.debug(f"Создатель монеты {self.address}: {creator}")
            
            return creator
            
        except TimeoutException:
            logger.error(f"На странице не найдена информация по создателю монеты {self.address}")
            
            return None
   
    def get_lp_locked(self):
        try:
            lp_locked_element = self.driver.find_element(
                By.XPATH,
                "//*[@id='token-show']/div/div[3]/div[2]/div/div[2]/table/tbody/tr[6]/td[2]"
            )
            lp_locked = float(lp_locked_element.text.strip("%"))
            logger.debug(f"Заблокированная ликвидности монеты {self.address}: {lp_locked}")
            
            return lp_locked
        
        except:
            logger.debug(f"У монеты {self.address} ликвидность не заблокирована")
            
            return None
