import logging
from typing import List, Dict, Any

# from nicepay_api import NicePayAPI
# from greengo_api import GreengoAPI
# from onlypays_api import OnlyPaysAPI
# from pspware_api import PSPWareAPI


logger = logging.getLogger(__name__)

class PaymentAPIManager:

    def __init__(self, apis: List[Dict[str, Any]] = None):
        # Инициализация и регистрация апи
        self.apis = apis or []

        # Добавляю NicePay API в список (по примеру остальных)
        # self.apis.append({
        #     "name": "NicePay",
        #     "api": NicePayAPI(),
        #     "pay_type_mapping": {}
        # })

        # Пример, если надо инициализировать остальные, можно раскомментировать
        # self.apis.extend([
        #    {"name": "Greengo", "api": GreengoAPI(), "pay_type_mapping": {}},
        #    {"name": "OnlyPays", "api": OnlyPaysAPI(config.ONLYPAYS_API_ID, config.ONLYPAYS_SECRET_KEY, config.ONLYPAYS_PAYMENT_KEY), "pay_type_mapping": {}},
        #    {"name": "PSPWare", "api": PSPWareAPI(), "pay_type_mapping": {}}
        # ])

    async def create_order(self, amount: int, payment_type: str, personal_id: str, is_sell_order: bool = False) -> Dict[str, Any]:
        for api_config in self.apis:
            api = api_config['api']
            api_name = api_config['name']
            pay_type_mapping = api_config.get('pay_type_mapping', {})
            mapped_payment_type = pay_type_mapping.get(payment_type, payment_type)

            try:
                if is_sell_order and api_name != 'OnlyPays':
                    continue

                if api_name == 'Greengo':
                    response = await api.create_order(
                        payment_method=mapped_payment_type,
                        wallet='',
                        from_amount=str(amount)
                    )
                elif api_name == 'PSPWare':
                    response = await api.create_order(
                        amount=amount,
                        pay_types=[mapped_payment_type],
                        personal_id=personal_id
                    )
                elif api_name == 'NicePay':
                    # Для NicePay используем personal_id == merchantOrderId, а payment_type - paymentMethod
                    response = await api.create_payment(
                        merchant_order_id=str(personal_id),
                        amount=amount,
                        payment_type=mapped_payment_type
                    )
                else:
                    response = await api.create_order(
                        amount=amount,
                        payment_type=mapped_payment_type,
                        personal_id=personal_id
                    )

                if response.get('success') or response.get('resultCode') == '0000':
                    response['api_name'] = api_name
                    if api_name == 'Greengo':
                        response['data'] = {
                            'id': response.get('order_id', personal_id),
                            'requisite': response.get('requisite', ''),
                            'owner': response.get('owner', 'Неизвестно'),
                            'bank': response.get('bank', 'Неизвестно')
                        }
                    elif api_name == 'NicePay':
                        # Вариант данных из response для NicePay по документации
                        # Можно взять paymentUrl для оплаты, transactionId и т.п.
                        response.setdefault('data', {})
                        response['data']['id'] = response.get('merchantOrderId', personal_id) or response['data'].get('merchantOrderId', personal_id)
                        response['data']['payment_url'] = response.get('paymentUrl') or response['data'].get('paymentUrl')
                        response['data']['status'] = response.get('resultCode')
                    return response
                else:
                    logger.warning(f"{api_name} не смог создать заказ: {response.get('error', response.get('resultDesc', 'Нет описания'))}")

            except Exception as e:
                logger.error(f"Ошибка при создании заказа через {api_name}: {e}")

        return {'success': False, 'error': 'Все платежные API не сработали', 'api_name': None}

    async def get_order_status(self, order_id: str, api_name: str) -> Dict[str, Any]:
        api_config = next((api for api in self.apis if api['name'] == api_name), None)
        if not api_config:
            return {'success': False, 'error': f"API {api_name} не найдено"}

        try:
            api = api_config['api']
            if api_name == 'Greengo':
                response = await api.check_order([order_id])
            elif api_name == 'NicePay':
                response = await api.get_payment_status(order_id)
            else:
                response = await api.get_order_status(order_id)

            response['api_name'] = api_name
            return response
        except Exception as e:
            logger.error(f"Ошибка проверки статуса через {api_name}: {e}")
            return {'success': False, 'error': str(e), 'api_name': api_name}

    async def cancel_order(self, order_id: str, api_name: str) -> Dict[str, Any]:
        api_config = next((api for api in self.apis if api['name'] == api_name), None)
        if not api_config:
            return {'success': False, 'error': f"API {api_name} не найдено"}

        try:
            api = api_config['api']
            if api_name == 'Greengo':
                response = await api.cancel_order([order_id])
            elif api_name == 'NicePay':
                response = await api.cancel_payment(order_id)
            else:
                response = await api.cancel_order(order_id)

            response['api_name'] = api_name
            return response
        except Exception as e:
            logger.error(f"Ошибка отмены заказа через {api_name}: {e}")
            return {'success': False, 'error': str(e), 'api_name': api_name}

    async def health_check(self) -> Dict[str, Dict[str, Any]]:
        results = {}
        for api_config in self.apis:
            api = api_config['api']
            api_name = api_config['name']
            try:
                response = await api.health_check()
                results[api_name] = response
            except Exception as e:
                results[api_name] = {'success': False, 'error': str(e)}
        return results
