import random
from aiogram import Router, types
from aiogram.filters import Command

from client.handlers.settings_client import fetch_bot_settings
from client.handlers.storage import user_data
from client.handlers.language import set_language_and_login, ask_language

router = Router()

EMOJIS = ['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼']

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    chat_id = message.chat.id

    # 1) Сбрасываем сессию
    user_data[chat_id] = {}

    # 2) Тянем настройки из БД (без токена)
    settings = await fetch_bot_settings()
    user_data[chat_id]['settings'] = settings

    # 3) Если нужна капча ‒ запустить, иначе сразу на выбор языка
    if settings.get('captcha_enabled'):
        user_data[chat_id]['step'] = 'captcha'
        target = random.choice(EMOJIS)
        user_data[chat_id]['captcha'] = target
        first = random.sample(EMOJIS, 4)
        second = [e for e in EMOJIS if e not in first]
        kb = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=e) for e in first],
                      [types.KeyboardButton(text=e) for e in second]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(f"Для безопасности выберите эмодзи {target}", reply_markup=kb)
    else:
        # пропускаем капчу
        user_data[chat_id]['step'] = 'show_language_keyboard'
        await ask_language(message)

@router.message(lambda msg: user_data.get(msg.chat.id, {}).get('step') == 'captcha')
async def check_captcha(message: types.Message):
    chat_id = message.chat.id
    data    = user_data[chat_id]

    if message.text == data['captcha']:
        # Правильно отгадал
        # Уберём клавиатуру капчи и перейдём к языку
        data['step'] = 'show_language_keyboard'
        await message.answer(
            "Отлично! Теперь выберите язык.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        # Показываем клавиатуру языков:
        from client.handlers.language import ask_language
        await ask_language(message)
    else:
        await message.answer("Неверно, попробуйте ещё раз.")
