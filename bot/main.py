from utils.settings import run_bot
import asyncio
from bot.logger import logger

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info('Бот остановлен')
