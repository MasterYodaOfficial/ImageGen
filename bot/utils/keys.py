import os
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
BOT_NAME = os.getenv('BOT_NAME')
KEY_IMAGE_GEN = os.getenv('KEY_IMAGE_GEN')