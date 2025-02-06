import logging
import random
from django.conf import settings

logger = logging.getLogger(__name__)


class BypassCloudflare:
    def __init__(self, browser):
        self.browser = browser

    async def check_cloudflare(self, page):
        """
        Проверяет наличие защиты Cloudflare.
        """
        
        await self.browser.wait(random.randint(1, 2))
        try:
            await page.find("Verifying you are human")
            await self._bypass_cloudflare(page)
        except:
            return None

    async def bypass_cloudflare(self, page):
        """
        Проходит Cloudflare с помощью расширения 2captcha.
        """
        
        try:
            captcha_solve_button = await page.find("Solve with 2captcha")
            await captcha_solve_button.click()
        except:
            logger.debug("Кнопка 2Captcha не найдена, повтор попытки")
            await page.reload()
            await self.bypass_cloudflare(page)
            
        while True:
            try:
                await page.find("Verifying you are human.")
                logger.debug("Ожидание ответа от 2captcha...")
                await self.browser.wait(5)
            except:
                break
            
        logger.info("Защита Cloudflare успешно пройдена")
        
    async def _get_2captcha_api_key(self):
        """
        Вводит API ключ для работы расширения 2captcha.
        """
        
        captcha_extenshion_page = await self.browser.get(settings.CAPTCHA_EXTENSION_LINK)
        api_key_input = await captcha_extenshion_page.select("input[name=apiKey]")
        
        await api_key_input.send_keys(settings.CAPTCHA_API_KEY)
        login_button = await captcha_extenshion_page.find("Login")
        await login_button.click()