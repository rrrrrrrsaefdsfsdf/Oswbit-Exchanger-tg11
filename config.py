import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен Telegram бота
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    BOT_MODE = os.getenv("BOT_MODE", 'polling')
    
    # Идентификатор API OnlyPays
    ONLYPAYS_API_ID = os.getenv("ONLYPAYS_API_ID")
    # Секретный ключ API OnlyPays
    ONLYPAYS_SECRET_KEY = os.getenv("ONLYPAYS_SECRET_KEY")
    ONLYPAYS_PAYMENT_KEY = os.getenv("ONLYPAYS_PAYMENT_KEY")
    
    # 🔧 API-доступы PSPWare
    PSPWARE_API_KEY = os.getenv("PSPWARE_API_KEY")
    PSPWARE_MERCHANT_ID = os.getenv("PSPWARE_MERCHANT_ID")
    
    # URL базы данных (по умолчанию SQLite)
    DATABASE_URL = os.getenv("DATABASE_URL", "oswaldo_exchanger.db")
    
    # ID администратора
    ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", 0))
    # ID чата администраторов
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))
    # ID чата операторов
    OPERATOR_CHAT_ID = int(os.getenv("OPERATOR_CHAT_ID", 0))
    
    # ID канала для отзывов
    REVIEWS_CHANNEL_ID = int(os.getenv("REVIEWS_CHANNEL_ID", 0))
    
    # Включение капчи при регистрации
    CAPTCHA_ENABLED = os.getenv("CAPTCHA_ENABLED", "true").lower() == "true"

    # Минимальная сумма обмена
    MIN_AMOUNT = int(os.getenv("MIN_AMOUNT", 1000))
    # Максимальная сумма обмена
    MAX_AMOUNT = int(os.getenv("MAX_AMOUNT", 500000))
    
    # Имя бота в Telegram
    BOT_USERNAME = os.getenv("BOT_USERNAME", "OswbitExchanger_bot")
    
    # Название обменника
    EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "Oswbit Exchanger")
    # Чат поддержки
    SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "@")
    # Менеджер поддержки
    SUPPORT_MANAGER = os.getenv("SUPPORT_MANAGER", "@")
    # Канал новостей
    NEWS_CHANNEL = os.getenv("NEWS_CHANNEL", "@")
    # Канал отзывов
    REVIEWS_CHANNEL = os.getenv("REVIEWS_CHANNEL", "@")

config = Config()