import aiohttp
import logging
from config import config

logger = logging.getLogger(__name__)

class PSPWareAPI:
    """Класс для работы с API v2 PSPWare"""

    def __init__(self):
        self.base_url = "https://api.pspware.space/merchant/v2"
        self.api_key = config.PSPWARE_API_KEY
        self.merchant_id = config.PSPWARE_MERCHANT_ID
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }









    async def create_order(self, amount: float, pay_types: list, personal_id: str, order_type: str = "PAY-IN", geos: list = None) -> dict:
            """
            Создание заказа в PSPWare API v2
            
            Args:
                amount: Сумма в рублях (число с плавающей точкой)
                pay_types: Список типов оплаты (например, ['sbp', 'c2c'])
                personal_id: Уникальный идентификатор заказа
                order_type: Тип операции ('PAY-IN' или 'PAY-OUT')
                geos: Список гео (например, ['RU', 'TJK']), по умолчанию ['RU']
            
            Returns:
                dict: Ответ от API с данными заказа или ошибкой
            """
            try:
                url = f"{self.base_url}/orders"
                payload = {
                    "sum": amount,
                    "currency": "RUB",
                    "order_type": order_type,
                    "pay_types": pay_types,
                    "geos": geos or ["RU"],
                    "merchant_id": self.merchant_id,
                    "order_id": personal_id,
                    "description": f"Exchange order {personal_id}"
                }
                
                # Логируем запрос для отладки
                logger.info(f"PSPWare create_order request: {payload}")
                
                if order_type == "PAY-OUT":
                    payload.pop("pay_types", None)
                    payload.pop("geos", None)
                    payload["bank"] = "any-bank"
                    
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=self.headers) as response:
                        response_data = await response.json()
                        
                        # Логируем ответ для отладки
                        logger.info(f"PSPWare create_order response: {response_data}")
                        
                        if response.status == 200 and response_data.get("status") == "success":
                            return {
                                "success": True,
                                "data": {
                                    "id": response_data.get("id"),
                                    "sum": response_data.get("sum"),  # Учитываем рандомизацию
                                    "requisite": response_data.get("card", ""),
                                    "owner": response_data.get("recipient", ""),
                                    "bank": response_data.get("bankName", ""),
                                    "pay_type": response_data.get("pay_type", ""),
                                    "payment_url": response_data.get("payment_url", None),
                                    "bik": response_data.get("bik", None),
                                    "geo": response_data.get("geo", ""),
                                    "status": response_data.get("status", "")
                                }
                            }
                        else:
                            # Улучшенная обработка ошибок
                            error_message = "Unknown error"
                            if response_data.get("detail"):
                                # Обработка ошибок валидации
                                if isinstance(response_data["detail"], list):
                                    errors = []
                                    for error in response_data["detail"]:
                                        field = ".".join(str(loc) for loc in error.get("loc", []))
                                        msg = error.get("msg", "Invalid value")
                                        errors.append(f"{field}: {msg}")
                                    error_message = "; ".join(errors)
                                else:
                                    error_message = str(response_data["detail"])
                            elif response_data.get("message"):
                                error_message = response_data["message"]
                            
                            logger.error(f"Failed to create order: {response_data}")
                            return {
                                "success": False, 
                                "error": error_message, 
                                "status_code": response.status,
                                "raw_response": response_data
                            }
            except Exception as e:
                logger.error(f"Create order error: {e}")
                return {"success": False, "error": str(e)}







    async def create_withdrawal(self, address: str, amount: float) -> dict:
        """
        Создание заявки на вывод средств в PSPWare API v2
        
        Args:
            address: Адрес для вывода средств
            amount: Сумма в рублях (число с плавающей точкой)
        
        Returns:
            dict: Ответ от API с данными заявки на вывод или ошибкой
        """
        try:
            url = f"{self.base_url}/withdrawal"
            payload = {
                "address": address,
                "sum": amount
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    response_data = await response.json()
                    if response.status == 200:
                        return {
                            "success": True,
                            "data": {
                                "id": response_data.get("id"),
                                "address": response_data.get("address"),
                                "sum": response_data.get("sum"),
                                "status": response_data.get("status"),
                                "merchant_id": response_data.get("merchantId"),
                                "created_at": response_data.get("createdAt"),
                                "updated_at": response_data.get("updatedAt")
                            }
                        }
                    else:
                        logger.error(f"Failed to create withdrawal: {response_data}")
                        return {"success": False, "error": response_data.get("message", "Unknown error"), "status_code": response.status}
        except Exception as e:
            logger.error(f"Create withdrawal error: {e}")
            return {"success": False, "error": str(e)}

    async def get_order_status(self, order_id: str) -> dict:
        """
        Получение статуса заказа
        
        Args:
            order_id: Идентификатор заказа в PSPWare
        
        Returns:
            dict: Ответ от API с данными статуса или ошибкой
        """
        try:
            url = f"{self.base_url}/orders/{order_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response_data = await response.json()
                    if response.status == 200:
                        return {
                            "success": True,
                            "data": {
                                "id": response_data.get("id"),
                                "sum": response_data.get("sum"),
                                "status": response_data.get("status"),
                                "requisite": response_data.get("card", ""),
                                "owner": response_data.get("recipient", ""),
                                "bank": response_data.get("bankName", ""),
                                "pay_type": response_data.get("pay_type", ""),
                                "payment_url": response_data.get("payment_url", None),
                                "bik": response_data.get("bik", None),
                                "geo": response_data.get("geo", ""),
                                "is_sbp": response_data.get("is_sbp", False)
                            }
                        }
                    else:
                        logger.error(f"Failed to get order status: {response_data}")
                        return {"success": False, "error": response_data.get("message", "Unknown error"), "status_code": response.status}
        except Exception as e:
            logger.error(f"Get order status error: {e}")
            return {"success": False, "error": str(e)}

    async def cancel_order(self, order_id: str) -> dict:
        """
        Отмена заказа в PSPWare API v2
        
        Args:
            order_id: Идентификатор заказа в PSPWare
        
        Returns:
            dict: Ответ от API с подтверждением отмены или ошибкой
        """
        try:
            url = f"{self.base_url}/orders/{order_id}/cancel"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers) as response:
                    response_data = await response.json()
                    if response.status == 200 and response_data.get("status") == "success":
                        return {"success": True, "data": {"id": order_id, "status": "canceled"}}
                    else:
                        logger.error(f"Failed to cancel order: {response_data}")
                        return {"success": False, "error": response_data.get("message", "Unknown error"), "status_code": response.status}
        except Exception as e:
            logger.error(f"Cancel order error: {e}")
            return {"success": False, "error": str(e)}

    async def get_merchant_info(self) -> dict:
        """
        Получение информации о мерчанте в PSPWare API v2
        
        Returns:
            dict: Ответ от API с данными мерчанта или ошибкой
        """
        try:
            url = f"{self.base_url}/merchant/me"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response_data = await response.json()
                    if response.status == 200:
                        return {
                            "success": True,
                            "data": {
                                "id": response_data.get("id"),
                                "name": response_data.get("name"),
                                "balance": response_data.get("balance"),
                                "hold_balance": response_data.get("hold_balance"),
                                "percents": response_data.get("percents", [])
                            }
                        }
                    else:
                        logger.error(f"Failed to get merchant info: {response_data}")
                        return {"success": False, "error": response_data.get("message", "Unknown error"), "status_code": response.status}
        except Exception as e:
            logger.error(f"Get merchant info error: {e}")
            return {"success": False, "error": str(e)}

    async def health_check(self) -> dict:
        """
        Проверка состояния сервиса PSPWare API v2
        
        Returns:
            dict: Ответ от API с состоянием сервиса или ошибкой
        """
        try:
            url = f"{self.base_url}/health"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response_data = await response.json()
                    if response.status == 200 and response_data.get("status") == "ok":
                        return {"success": True, "data": {"status": "ok"}}
                    else:
                        logger.error(f"Health check failed: {response_data}")
                        return {"success": False, "error": response_data.get("message", "Service unhealthy"), "status_code": response.status}
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {"success": False, "error": str(e)}