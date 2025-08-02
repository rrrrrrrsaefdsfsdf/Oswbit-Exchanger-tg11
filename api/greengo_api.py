import logging
import aiohttp
from config import config

logger = logging.getLogger(__name__)

class GreengoAPI:
    def __init__(self):
        self.api_secret = config.GREENGO_API_SECRET
        self.base_url = "https://api.greengo.cc/api/v2"
        self.headers = {
            "Api-Secret": self.api_secret,
            "Content-Type": "application/json"
        }


    async def create_order(self, payment_method: str, wallet: str, from_amount: str):
        url = f"{self.base_url}/order/create"
        data = {
            "payment_method": payment_method,
            "wallet": wallet,
            "from_amount": from_amount
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=self.headers) as response:
                    result = await response.json()
                    logger.info(f"Greengo create_order ответ: {result}")
                    return result
        except Exception as e:
            logger.error(f"Greengo create_order ошибка: {e}")
            return {"success": False, "error": str(e)}


    async def get_directions(self):
        url = f"{self.base_url}/directions"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    result = await response.json()
                    logger.info(f"Greengo get_directions ответ: {result}")
                    return result
        except Exception as e:
            logger.error(f"Greengo get_directions ошибка: {e}")
            return {"success": False, "error": str(e)}


    async def check_order(self, order_ids: list[str]):
        url = f"{self.base_url}/order/check"
        data = {"order_id": order_ids}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=self.headers) as response:
                    result = await response.json()
                    logger.info(f"Greengo check_order ответ: {result}")
                    return result
        except Exception as e:
            logger.error(f"Greengo check_order ошибка: {e}")
            return {"success": False, "error": str(e)}


    async def cancel_order(self, order_ids: list[str]):
        url = f"{self.base_url}/order/cancel"
        data = {"order_id": order_ids}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=self.headers) as response:
                    result = await response.json()
                    logger.info(f"Greengo cancel_order ответ: {result}")
                    return result
        except Exception as e:
            logger.error(f"Greengo cancel_order ошибка: {e}")
            return {"success": False, "error": str(e)}