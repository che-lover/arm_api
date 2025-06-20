import os, httpx
from aiogram import Router, types

from client.handlers.flow import main_menu_router, make_main_menu
from client.handlers.storage import user_data

router = Router()
API_BASE = os.getenv('API_BASE_URL')
LANG_BTN = {
    'ru': '🇷🇺 Русский',
    'hy': '🇦🇲 Հայերեն',
    'en': '🇬🇧 English',
}

# 1) Показываем клавиатуру ровно на один раз
@router.message(lambda msg: user_data.get(msg.chat.id, {}).get('step') == 'show_language_keyboard')
async def ask_language(message: types.Message):
    chat_id = message.chat.id
    data    = user_data[chat_id]
    # сразу переключаемся на стадию «ждём выбор»
    data['step'] = 'await_language'

    buttons = [[ types.KeyboardButton(text=v) for v in LANG_BTN.values() ]]
    kb = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "Выберите язык / Ընտրեք լեզուն / Choose language",
        reply_markup=kb
    )

# 2) Обрабатываем нажатие кнопки языка только в этом состоянии
@router.message(lambda msg:
    user_data.get(msg.chat.id, {}).get('step') == 'await_language'
    and msg.text in LANG_BTN.values()
)
async def set_language_and_login(message: types.Message):
    chat_id = message.chat.id
    code = next(k for k,v in LANG_BTN.items() if v == message.text)
    data = user_data[chat_id]
    data['lang'] = code

    # тут ваш /auth/bot-login, получаем token и user_id
    async with httpx.AsyncClient() as cli:
        resp = await cli.post(f"{os.getenv('API_BASE_URL')}/v1/auth/bot-login",
                              json={'telegram_id': chat_id})
    payload = resp.json().get('data') or {}
    data['token']   = payload.get('token')
    data['user_id'] = payload.get('user',{}).get('id')

    # После авторизации показываем главное меню,
    # но перед этим проверяем подписку на канал из settings
    channel = data['settings'].get('channel_link')
    if channel:
        try:
            member = await message.bot.get_chat_member(chat_id=channel, user_id=chat_id)
            if member.status in ('left','kicked'):
                return await message.answer(
                    f"🔔 Подпишитесь на канал {channel} для скидки"
                )
        except:
            pass

    data['step'] = 'main'
    kb = make_main_menu(code)
    await message.answer(
        {'ru':'Выберите действие:','hy':'Ընտրեք գործողությունը:','en':'Choose action:'}[code],
        reply_markup=kb
    )
