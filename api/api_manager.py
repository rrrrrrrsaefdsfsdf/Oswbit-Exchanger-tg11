import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class PaymentAPIManager:
    def __init__(self, apis: List[Dict[str, Any]]):
        self.apis = apis
    




    async def create_order(self, amount: int, payment_type: str, personal_id: str, is_sell_order: bool = False) -> Dict[str, Any]:
        for api_config in self.apis:
            api = api_config['api']
            api_name = api_config['name']
            pay_type_mapping = api_config.get('pay_type_mapping', {})
            mapped_payment_type = pay_type_mapping.get(payment_type, payment_type)
            
            logger.info(f"Вызов create_order для {api_name} с параметрами: amount={amount}, pay_types={[mapped_payment_type] if api_name == 'PSPWare' else mapped_payment_type}, personal_id={personal_id}")
            
            try:
                if is_sell_order and api_name != 'OnlyPays':
                    continue
                    
                logger.info(f"Попытка создания заказа через {api_name} (тип платежа: {payment_type} -> {mapped_payment_type})")
                
                if api_name == 'Greengo':
                    response = await api.create_order(
                        payment_method=mapped_payment_type,
                        wallet='',
                        from_amount=str(amount)
                    )
                elif api_name == 'PSPWare':
                    response = await api.create_order(
                        amount=amount,
                        pay_types=[mapped_payment_type],  # Передаём как список
                        personal_id=personal_id
                    )
                else:
                    response = await api.create_order(
                        amount=amount,
                        payment_type=mapped_payment_type,
                        personal_id=personal_id
                    )
                    
                if response.get('success'):
                    response['api_name'] = api_name
                    if api_name == 'Greengo':
                        response['data'] = {
                            'id': response.get('order_id', personal_id),
                            'requisite': response.get('requisite', ''),
                            'owner': response.get('owner', 'Неизвестно'),
                            'bank': response.get('bank', 'Неизвестно')
                        }
                    return response
                else:
                    logger.warning(f"{api_name} не смог создать заказ: {response.get('error')}")
                
            except Exception as e:
                logger.error(f"Ошибка при создании заказа через {api_name}: {e}")
                response = {'success': False, 'error': str(e), 'api_name': api_name}
            
        return {'success': False, 'error': 'Все платежные API не сработали', 'api_name': 'None'}






    async def get_order_status(self, order_id: str, api_name: str) -> Dict[str, Any]:
        api_config = next((api for api in self.apis if api['name'] == api_name), None)
        if not api_config:
            return {'success': False, 'error': f"API {api_name} не найдено"}
        
        try:
            if api_name == 'Greengo':
                response = await api_config['api'].check_order([order_id])
            else:
                response = await api_config['api'].get_order_status(order_id)
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
            if api_name == 'Greengo':
                response = await api_config['api'].cancel_order([order_id])
            else:
                response = await api_config['api'].cancel_order(order_id)
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