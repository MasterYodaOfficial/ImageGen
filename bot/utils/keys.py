import os
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
BOT_NAME = os.getenv('BOT_NAME')
KEY_IMAGE_GEN = os.getenv('KEY_IMAGE_GEN')
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
KEY_OPENAI = os.getenv('KEY_OPENAI')
ADMIN_NAME = os.getenv('ADMIN_NAME')
DEFAULT_GIFT_TOKENS = int(os.getenv("DEFAULT_GIFT_TOKENS", 0))
