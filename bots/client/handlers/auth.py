import os
import httpx
from aiogram import Router, types
from aiogram import F
from client.handlers.storage import user_data

router = Router()
API_BASE = os.getenv('API_BASE_URL') # например, http://laravel-app:80/api
TOKEN_KEY = 'token'

# @router.message(Text(equals=['🔑 Войти','🔑 Մուտք գործել','🔑 Login']))
@router.message(F.text.in_(['🔑 Войти','🔑 Մուտք գործել','🔑 Login']))
async def bot_login(message: types.Message):
    chat_id = message.chat.id
    data = user_data.get(chat_id, {})
    lang = data.get('lang','en')
    telegram_id = message.from_user.id

    async with httpx.AsyncClient() as client:
        # делаем POST на /auth/bot-login
        resp = await client.post(f"{API_BASE}/auth/bot-login", json={'telegram_id': telegram_id})

    if resp.status_code == 200 and resp.json().get('token'):
        token = resp.json()['token']
        data[TOKEN_KEY] = token
        data['step'] = 'main'
        await message.answer({
            'ru': 'Успешно! Вы вошли.',
            'hy': 'Ձեր մուտքը հաջողվեց։',
            'en': 'Logged in successfully.'
        }[lang], reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer({
            'ru': 'Ошибка входа, попробуйте ещё раз.',
            'hy': 'Մուտքի սխալ, փորձեք կրկին։',
            'en': 'Login failed, please try again.'
        }[lang])
