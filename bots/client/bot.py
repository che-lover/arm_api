import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

API_BASE_URL = os.getenv('API_BASE_URL')
TOKEN        = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в .env")

logging.basicConfig(level=logging.INFO)


# создаём бота и диспетчер с in-memory FSM
bot = Bot(token=TOKEN, parse_mode='HTML')
dp  = Dispatcher(storage=MemoryStorage())

from client.handlers.captcha  import router as captcha_router
from client.handlers.language import router as language_router
from client.handlers.auth     import router as auth_router
from client.handlers.flow     import router as flow_router

dp.include_router(captcha_router)
dp.include_router(language_router)
dp.include_router(auth_router)
dp.include_router(flow_router)

if __name__ == '__main__':
    logging.info("🚀 Запускаем client-bot...")
    dp.run_polling(bot)
