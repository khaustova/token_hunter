import time
from datetime import datetime
from urllib.parse import urljoin

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from .models import SolscanResult

from dex_parser.logger import get_logger


logger = get_logger(__name__)


class SolscanParser:
    def __init__(self, address):
        self.url = "https://solscan.io/account/"
        self.address = address
        self.driver = None

    def __enter__(self):
        logger.info("Entering to the browser...")

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--headless")

        self.driver = uc.Chrome(use_subprocess=True, options=chrome_options)

        return self

    def __exit__(self, exc_type, exc_value, _):
        logger.info("Exiting from the browser...")
        if exc_type:
            logger.error(f"An exception occurred: {exc_value}")

        if self.driver:
            self.driver.close()

        return False

    def proccess_result(self, result: SolscanResult, elem: WebElement) -> SolscanResult:
        logger.debug(f"Trying process SOL for {result.address}: {elem.text}")
        if elem:
            result.temp_text = elem.text

        return result

    def parse_values(self, result: SolscanResult, driver) -> SolscanResult:
        logger.debug(f"Trying parse SOL for {result.address}")
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    (
                        "//div[text()='SOL Balance']/following::div"
                    ),
                )
            )
        )
        result = self.proccess_result(result, element)

        return result
    

    def fix_cf_just_moment(self, url: str, driver):
        # Fix CF `Just moment...` loading
        driver.execute_script(f"window.open('{url}', '_blank')")
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)
        driver.close()


    def get_parse_result(self, address: str) -> SolscanResult:
        if not self.driver:
            msg = "Please use context for the `SolscanParser`"
            logger.critical(msg)
            raise ValueError(msg)
        address = self.address
        result = SolscanResult(date=datetime.now(), address=address)
        url = urljoin(self.url, address)

        logger.info(f"Try parse: {result.address}")

        driver = self.driver
        driver.get(url)

        #self.fix_cf_just_moment(url, driver)
        
        driver.execute_script(f"window.open('{url}', '_blank')")
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)
        driver.close() 
        driver.switch_to.window(driver.window_handles[0])

        try:
            result = self.parse_values(result, driver)
        except TimeoutException:
            logger.info(f"Can't found SQL Balance or Token values: {result.address}")
            pass

        return result
