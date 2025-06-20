import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')
TOKEN_ADMIN   = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN_ADMIN or not API_BASE_URL:
    raise RuntimeError("Не заданы TELEGRAM_BOT_TOKEN или API_BASE_URL в .env")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN_ADMIN, parse_mode='HTML')
dp  = Dispatcher(storage=MemoryStorage())

# Подключаем роутеры
from admin.handlers.auth      import router as auth_router
from admin.handlers.menu      import router as menu_router
from admin.handlers.locations import router as locations_router
from admin.handlers.showcase import  router as showcase_router
from admin.handlers.coupons import router as coupons_router
from admin.handlers.roles import router as roles_router
from admin.handlers.finances import router as finances_router
from admin.handlers.settings import router as settings_router

dp.include_router(auth_router)
dp.include_router(menu_router)
dp.include_router(locations_router)
dp.include_router(showcase_router)
dp.include_router(coupons_router)
dp.include_router(roles_router)
dp.include_router(finances_router)
dp.include_router(settings_router)

if __name__ == '__main__':
    logging.info("🚀 Запускаем admin-bot...")
    dp.run_polling(bot)
