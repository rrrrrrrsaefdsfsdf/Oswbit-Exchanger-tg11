import logging
import hashlib
import time
import aiohttp
from config import config

logger = logging.getLogger(__name__)

class NicePayAPI:
    def __init__(self):
        self.merchant_key = config.NICEPAY_MERCHANT_KEY
        self.merchant_token_key = config.NICEPAY_MERCHANT_TOKEN_KEY
        self.base_url = "https://api.nicepay.io/v2/merchant"

    def _generate_merchant_token(self, params: dict) -> str:
        # Формируем строку токена: merchantKey + merchantOrderId + amount + merchantTokenKey
        token_string = (
            str(params.get("merchantKey", "")) +
            str(params.get("merchantOrderId", "")) +
            str(params.get("amount", "")) +
            self.merchant_token_key
        )
        return hashlib.sha256(token_string.encode("utf-8")).hexdigest()

    async def create_payment(self, merchant_order_id: str, amount: int, currency: str = "IDR",
                             payment_type: str = "01", description: str = "") -> dict:
        url = f"{self.base_url}/payment/request"
        timestamp = int(time.time() * 1000)
        params = {
            "merchantKey": self.merchant_key,
            "merchantOrderId": merchant_order_id,
            "amount": amount,
            "currency": currency,
            "paymentMethod": payment_type,
            "timestamp": timestamp,
            "description": description,
        }
        params["merchantToken"] = self._generate_merchant_token(params)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, headers=headers) as resp:
                    result = await resp.json()
                    logger.info(f"NicePay create_payment response: {result}")
                    return result
        except Exception as e:
            logger.error(f"NicePay create_payment error: {e}")
            return {"success": False, "error": str(e)}

    async def get_payment_status(self, merchant_order_id: str) -> dict:
        url = f"{self.base_url}/payment/status"
        timestamp = int(time.time() * 1000)
        params = {
            "merchantKey": self.merchant_key,
            "merchantOrderId": merchant_order_id,
            "timestamp": timestamp,
        }
        params["merchantToken"] = self._generate_merchant_token(params)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, headers=headers) as resp:
                    result = await resp.json()
                    logger.info(f"NicePay get_payment_status response: {result}")
                    return result
        except Exception as e:
            logger.error(f"NicePay get_payment_status error: {e}")
            return {"success": False, "error": str(e)}

    async def cancel_payment(self, merchant_order_id: str) -> dict:
        url = f"{self.base_url}/payment/cancel"
        timestamp = int(time.time() * 1000)
        params = {
            "merchantKey": self.merchant_key,
            "merchantOrderId": merchant_order_id,
            "timestamp": timestamp,
        }
        params["merchantToken"] = self._generate_merchant_token(params)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, headers=headers) as resp:
                    result = await resp.json()
                    logger.info(f"NicePay cancel_payment response: {result}")
                    return result
        except Exception as e:
            logger.error(f"NicePay cancel_payment error: {e}")
            return {"success": False, "error": str(e)}
