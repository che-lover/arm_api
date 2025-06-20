import os
import logging
import urllib.parse

import httpx
from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from io import BytesIO
from aiogram.types import InputFile
from client.handlers.storage import user_data
from client.handlers.settings_client import fetch_bot_settings

router = Router()
API_BASE = os.getenv('API_BASE_URL', 'http://138.124.123.68:8080/api')
API_V1 = API_BASE.rstrip('/') + '/v1'

DASH_RATE = float(os.getenv('DASH_EXCHANGE_RATE', '0.001'))

logging.getLogger(__name__).setLevel(logging.DEBUG)

PURCHASE_BTN = ['🛒 Купить', '🛒 Գնել', '🛒 Buy']
MENU_BTN = {
    'purchase': {'ru': '🛒 Купить', 'hy': '🛒 Գնել', 'en': '🛒 Buy'},
    'operator': {'ru': '📞 Оператор', 'hy': '📞 Օպերատոր', 'en': '📞 Operator'},
    'how_to_buy': {'ru': '❓ Как купить', 'hy': '❓ Ինչպես գնել', 'en': '❓ How to buy'},
    'change_lang': {'ru': '🌐 Сменить язык', 'hy': '🌐 Փոխել լեզուն', 'en': '🌐 Change language'},
    'discount': {'ru': '💸 Скидка', 'hy': '💸 Զեղչ', 'en': '💸 Discount'},
    'reviews': {'ru': '📝 Отзывы', 'hy': '📝 Վերլուծություններ', 'en': '📝 Reviews'},
    'menu': {'ru': '📋 Меню', 'hy': '📋 Մենյու', 'en': '📋 Menu'}
}
BACK_BTN = {'ru': '🔙 Назад', 'hy': '🔙 Անհետ', 'en': '🔙 Back'}
MENU_BTN_EXTRA = {'ru': '📋 Меню', 'hy': '📋 Մենյու', 'en': '📋 Menu'}

CHANNEL_USERNAME = os.getenv('TELEGRAM_CHANNEL', '@your_channel')


def make_keyboard(rows: list[list[str]], lang: str, with_back=True, with_menu=True):
    kb_rows = [[KeyboardButton(text=label) for label in row] for row in rows]
    extra = []
    if with_back:
        extra.append(BACK_BTN[lang])
    if with_menu:
        extra.append(MENU_BTN_EXTRA[lang])
    if extra:
        kb_rows.append([KeyboardButton(text=t) for t in extra])
    return ReplyKeyboardMarkup(keyboard=kb_rows, resize_keyboard=True)


def make_main_menu(lang: str) -> ReplyKeyboardMarkup:
    # собираем кнопки из словаря MENU_BTN
    labels = [
        MENU_BTN['purchase'][lang],
        MENU_BTN['operator'][lang],
        MENU_BTN['how_to_buy'][lang],
        MENU_BTN['change_lang'][lang],
        MENU_BTN['discount'][lang],
        MENU_BTN['reviews'][lang],
        MENU_BTN['menu'][lang],
    ]
    # делим на строки по 2 кнопки
    keyboard = []
    for i in range(0, len(labels), 2):
        row = [KeyboardButton(text=labels[i])]
        if i + 1 < len(labels):
            row.append(KeyboardButton(text=labels[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


@router.message(
    F.text.in_([
        MENU_BTN_EXTRA['ru'],
        MENU_BTN_EXTRA['hy'],
        MENU_BTN_EXTRA['en'],
    ])
)
async def show_main_menu(message: types.Message):
    chat_id = message.chat.id
    data = user_data[chat_id]
    lang = data['lang']
    # сбрасываем состояние цепочки
    data['step'] = 'main'
    await message.answer(
        {
            'ru': '📋 Главное меню:',
            'hy': '📋 Գլխավոր մենյու՝',
            'en': '📋 Main menu:'
        }[lang],
        reply_markup=make_main_menu(lang)
    )


@router.message(
    # lambda m: user_data.get(m.chat.id, {}).get('step') == 'main',
    F.text.in_([label for sub in MENU_BTN.values() for label in sub.values()])
)
async def main_menu_router(message: types.Message):
    chat_id = message.chat.id
    data = user_data[chat_id]
    lang = data['lang']
    text = message.text

    # проверяем что нажали
    if text == MENU_BTN['purchase'][lang]:
        # → покупка
        data['step'] = 'city_choose'
        await choose_city(message)  # вызываем ваш хендлер
    elif text == MENU_BTN['operator'][lang]:
        token = data['token']
        settings = await fetch_bot_settings()
        contact = settings.get('operator_contact') or '—'
        data['step'] = 'main'
        await message.answer({
                                 'ru': f'📞 Оператор: {contact}',
                                 'hy': f'📞 Օպերատոր: {contact}',
                                 'en': f'📞 Operator: {contact}'
                             }[lang])
    elif text == MENU_BTN['how_to_buy'][lang]:
        token = data['token']
        settings = await fetch_bot_settings()
        url = settings.get('exchange_url') or 'https://example.com'
        btn = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text={'ru': 'Перейти к обменнику', 'hy': 'Գնալ փոխանակիչ', 'en': 'Go to exchange'}[
                    lang],
                url=url
            )
        ]])
        data['step'] = 'main'
        await message.answer({
                                 'ru': '❓ Чтобы купить, перейдите по ссылке:',
                                 'hy': '❓ Գնելու համար անցեք հղումով՝',
                                 'en': '❓ To purchase, follow the link:'
                             }[lang], reply_markup=btn)
    elif text == MENU_BTN['change_lang'][lang]:
        data['step'] = 'main'
        # → переход к выбору языка
        data['step'] = 'show_language_keyboard'
        from client.handlers.language import ask_language
        await ask_language(message)
        return
    elif text == MENU_BTN['discount'][lang]:
        token = data['token']
        settings = await fetch_bot_settings()
        chan_link = settings.get('channel_link') or '—'

        if chan_link.startswith('http'):
            # https://t.me/your_channel  →  your_channel
            from urllib.parse import urlparse
            path = urlparse(chan_link).path  # '/your_channel'
            username = '@' + path.lstrip('/')
        else:
            username = chan_link if chan_link.startswith('@') else f"@{chan_link}"
        subscribed = False

        try:
            member = await message.bot.get_chat_member(chat_id=username, user_id=chat_id)
            # статусы 'member', 'administrator', 'creator' означают, что человек в канале
            if member.status in ('member', 'administrator', 'creator'):
                subscribed = True
        except Exception as e:
            # логируем, чтобы понять что-то пошло не так
            logging.warning("Cannot check subscription for %s: %r", username, e)

        # Сохраняем флаг в data, чтобы потом проставился в pay_payload
        data['apply_subscription_discount'] = subscribed

        # 2) Формируем текст ответа
        if subscribed:
            status_text = {
                'ru': '✅ Вы уже подписаны — ваша $2 скидка активна!',
                'hy': '✅ Դուք արդեն գրանցված եք — $2 զեղչը գործում է:',
                'en': '✅ You are subscribed — your $2 discount is active!'
            }[lang]
        else:
            status_text = {
                'ru': '⚠️ Вы не подписаны на канал, подпишитесь, чтобы получить скидку $2.',
                'hy': '⚠️ Դուք չեք գրանցված ալիքում, գրանցվեք՝ $2 զեղչի համար։',
                'en': '⚠️ You are not subscribed to the channel. Subscribe to get a $2 discount.'
            }[lang]

        data['step'] = 'main'
        await message.answer(
            f"{status_text}\n\n" + {
                'ru': 'Подпишитесь здесь:',
                'hy': 'Գրանցվեք այստեղ՝',
                'en': 'Subscribe here:'
            }[lang] + f" {chan_link}"
        )
    elif text == MENU_BTN['reviews'][lang]:
        data['step'] = 'main'
        await message.answer({
                                 'ru': 'Отзывы наших клиентов…',
                                 'hy': 'Մեր հաճախորդների կարծիքները…',
                                 'en': 'Customer reviews…'
                             }[lang])
    else:
        # непредвиденный текст
        await message.answer({
                                 'ru': 'Пожалуйста, выберите пункт меню.',
                                 'hy': 'Խնդրում ենք ընտրել առարկան.',
                                 'en': 'Please choose a menu item.'
                             }[lang])
        return


@router.message(
    lambda msg: user_data.get(msg.chat.id, {}).get('step') == 'city_choose',
    F.text.in_(list(MENU_BTN['purchase'].values()))
)
async def choose_city(message: types.Message):
    chat_id = message.chat.id
    data = user_data[chat_id]
    lang = data['lang']
    token = data['token']

    logging.debug(f"choose_city fired: step={data['step']} text={message.text!r}")

    # Inline-кнопки с городами
    async with httpx.AsyncClient(headers={'Authorization': f'Bearer {token}'}) as client:
        resp = await client.get(f"{API_V1}/cities")
        resp.raise_for_status()

    cities = resp.json()['data']
    buttons = [
        [InlineKeyboardButton(text=city[f'name_{lang}'], callback_data=f'city:{city["id"]}')]
        for city in cities
    ]
    buttons.append([InlineKeyboardButton(text={'ru': '🔙 Назад', 'en': '🔙 Back'}[lang], callback_data='back_to_main')])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer({
                             'ru': 'Выберите город:',
                             'hy': 'Ընտրեք քաղաքը:',
                             'en': 'Select a city:'
                         }[lang], reply_markup=kb)

    data['step'] = 'city'


@router.callback_query(lambda c: c.data and c.data.startswith('city:'))
async def on_city_selected(call: types.CallbackQuery):
    chat_id = call.from_user.id
    data = user_data[chat_id]
    lang = data['lang']
    token = data['token']
    city_id = int(call.data.split(":", 1)[1])
    data['city_id'] = city_id

    # Теперь запрашиваем районы
    async with httpx.AsyncClient(
        headers={'Authorization': f'Bearer {token}'}
    ) as client:
        resp = await client.get(f"{API_V1}/districts?city_id={city_id}")
        resp.raise_for_status()
    districts = resp.json()['data']

    buttons = [
        [InlineKeyboardButton(text=d[f'name_{lang}'], callback_data=f'district:{d["id"]}')]
        for d in districts
    ]
    buttons.append([InlineKeyboardButton(text={'ru': '🔙 Назад к городам'}[lang], callback_data='back_to_cities')])
    buttons.append([InlineKeyboardButton(text={'ru': '❌ Отмена'}[lang], callback_data='back_to_main')])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await call.message.edit_text(
        {
            'ru': 'Выберите район:',
            'hy': 'Ընտրեք թաղամասը:',
            'en': 'Select a district:'
        }[lang],
        reply_markup=kb
    )
    data['step'] = 'district'
    await call.answer()


@router.callback_query(lambda c: c.data and c.data.startswith('product:'))
async def choose_packaging(call: types.CallbackQuery):
    chat_id = call.from_user.id
    data = user_data[chat_id]
    lang = data['lang']
    product_id = int(call.data.split(':', 1)[1])
    data['product_id'] = product_id
    token = data['token']

    # ——— берем список фасовок ———
    params = {
        'city_id': data['city_id'],
        'district_id': data['district_id'],
        'product_id': product_id,
    }
    async with httpx.AsyncClient(
        headers={'Authorization': f'Bearer {token}'}
    ) as client:
        resp = await client.get(f"{API_V1}/packagings", params=params)
        resp.raise_for_status()

    packagings = resp.json()['data']
    # оставляем только те, что относятся к нашему продукту
    buttons = [
        [InlineKeyboardButton(
            text=f"{pkg['volume']} — {pkg['price']}$",
            callback_data=f'packaging:{pkg["id"]}'
        )]
        for pkg in packagings
        if pkg['product_id'] == product_id
    ]
    buttons.append([InlineKeyboardButton(text='🔙 Назад к товарам', callback_data='back_to_products')])
    buttons.append([InlineKeyboardButton(text='❌ Отмена', callback_data='back_to_main')])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await call.message.edit_text(
        {
            'ru': 'Выберите фасовку:',
            'hy': 'Ընտրեք փաթեթավորումը:',
            'en': 'Select packaging:'
        }[lang],
        reply_markup=kb
    )
    data['step'] = 'packaging'
    await call.answer()


@router.callback_query(lambda c: c.data and c.data.startswith('packaging:'))
async def ask_quantity(call: types.CallbackQuery):
    chat_id = call.from_user.id
    data = user_data[chat_id]
    packaging_id = int(call.data.split(':', 1)[1])
    data['packaging_id'] = packaging_id
    data['step'] = 'quantity'

    lang = data['lang']
    volume = call.message.reply_markup.inline_keyboard[0][0].text.split('—')[0].strip()

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text={'ru': '✅ Подтвердить покупку', 'hy': '✅ Հաստատել కొనք', 'en': '✅ Confirm purchase'}[lang],
            callback_data='confirm_qty'
        ),
        InlineKeyboardButton(
            text={'ru': '🔙 Назад', 'hy': '🔙 Վերադարձի', 'en': '🔙 Back'}[lang],
            callback_data='cancel_qty'
        ),
    ]])

    await call.message.edit_text(
        {
            'ru': f"\nНажмите «Подтвердить покупку», чтобы продолжить.",
            'hy': f"\nՍեղմեք «Հաստատել գնումը» շարունակելու համար։",
            'en': f"\nClick “Confirm purchase” to proceed."
        }[lang],
        reply_markup=kb
    )
    await call.answer()


@router.callback_query(lambda c: c.data == 'confirm_qty')
async def on_confirm_qty(call: types.CallbackQuery):
    chat_id = call.from_user.id
    data = user_data[chat_id]
    lang = data['lang']

    # переводим шаг на ввод кода
    data['step'] = 'enter_coupon'

    # клавиатура: Ввести код / Пропустить
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text={'ru': 'Ввести код', 'hy': 'Գրել կոդը', 'en': 'Enter code'}[lang],
                             callback_data='coupon:enter'),
        InlineKeyboardButton(text={'ru': 'Пропустить', 'hy': 'Ֆ ռապսկիպ', 'en': 'Skip'}[lang],
                             callback_data='coupon:skip'),
    ]])

    await call.message.answer({
                                  'ru': 'Если у вас есть промо-код, введите его или нажмите «Пропустить»:',
                                  'hy': 'Եթե ունեք թարմացուցիչ կոդ, մուտքագրեք կամ սեղմեք «Ֆռապսկիպ»՝',
                                  'en': 'If you have a promo code, enter it now or press “Skip”:'
                              }[lang], reply_markup=kb)
    await call.answer()

@router.callback_query(lambda c: c.data and c.data.startswith('coupon:'))
async def on_coupon_choice(call: types.CallbackQuery):
    chat_id = call.from_user.id
    data = user_data[chat_id]
    lang = data['lang']
    action = call.data.split(':',1)[1]

    if action == 'enter':
        # попросить ввести сам код текстом
        data['step'] = 'awaiting_coupon_code'
        await call.message.answer({
            'ru': 'Пожалуйста, отправьте текст вашего промо-кода:',
            'hy': 'Խնդրում ենք ուղարկել ձեր թարմացման կոդը՝',
            'en': 'Please send your promo code as text:'
        }[lang])
        await call.answer()
    else:
        # пропуск — сразу к оплате
        data.pop('coupon_id', None)
        data['step'] = 'awaiting_payment'
        await create_order_item_and_pay(call.message)
        await call.answer()

@router.message(lambda m: user_data.get(m.chat.id,{}).get('step')=='awaiting_coupon_code')
async def receive_coupon_code(message: types.Message):
    chat_id = message.chat.id
    data = user_data[chat_id]
    lang = data['lang']
    text = message.text.strip()

    # сохраняем код (ожидаем, что это ID купона или его текстовая форма)
    # если нужен ID, можно попытаться int(text)
    data['coupon_id'] = message.text.strip()

    # переходим к оплате
    data['step'] = 'awaiting_payment'
    await message.answer({
        'ru': 'Промо-код установлен, продолжаем к оплате…',
        'hy': 'Թարմացման կոդը սահմանված է, շարունակենք վճարմանը…',
        'en': 'Promo code set, proceeding to payment…'
    }[lang])
    await create_order_item_and_pay(message)

@router.callback_query(lambda c: c.data == 'cancel_qty')
async def on_cancel_qty(call: types.CallbackQuery):
    chat_id = call.from_user.id
    data = user_data[chat_id]
    lang = data['lang']
    token = data['token']

    # заново запрашиваем список фасовок
    params = {
        'city_id': data['city_id'],
        'district_id': data['district_id'],
        'product_id': data['product_id'],
    }
    async with httpx.AsyncClient(
        headers={'Authorization': f'Bearer {token}'}
    ) as client:
        resp = await client.get(f"{API_V1}/packagings", params=params)
        resp.raise_for_status()
    packagings = resp.json()['data']

    # строим клавиатуру так же, как в choose_packaging
    buttons = [
        [InlineKeyboardButton(
            text=f"{pkg['volume']} — {pkg['price']}$",
            callback_data=f'packaging:{pkg["id"]}'
        )]
        for pkg in packagings
        if pkg['product_id'] == data['product_id']
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    # редактируем сообщение, чтобы юзер увидел заново ассортимент фасовок
    await call.message.edit_text(
        {
            'ru': 'Выберите фасовку:',
            'hy': 'Ընտրեք փաթեթավորումը:',
            'en': 'Select packaging:'
        }[lang],
        reply_markup=kb
    )

    # возвращаем шаг в сторедж
    data['step'] = 'packaging'
    await call.answer()


# @router.message(lambda m: user_data.get(m.chat.id, {}).get('step') == 'quantity')
@router.callback_query(lambda c: user_data.get(c.from_user.id, {}).get('step') == 'awaiting_payment')
async def create_order_item_and_pay(message: types.Message):
    chat_id = message.chat.id
    data = user_data[chat_id]
    lang = data['lang']
    token = data['token']
    qty = 1

    # 2) создаём позицию заказа
    payload = {
        'order_id': data['order_id'],
        'packaging_id': data['packaging_id'],
        'quantity': qty,
    }
    async with httpx.AsyncClient(
        headers={'Authorization': f'Bearer {token}'}
    ) as client:
        resp = await client.post(f"{API_V1}/order-items", json=payload)
        resp.raise_for_status()
    item = resp.json()['data']

    data['stash_id'] = item['inventory_id']

    # 3) вычисляем локальную сумму и конвертим в DASH
    pay_payload = {
        'order_id': data['order_id'],
        'coupon_id': data['coupon_id'],
        'apply_subscription_discount': data.get('apply_subscription_discount', False),
    }
    logging.info("PAYLOAD → %r", pay_payload)
    async with httpx.AsyncClient(
        headers={'Authorization': f'Bearer {token}'}
    ) as client:
        pay_resp = await client.post(f"{API_V1}/payments/create", json=pay_payload)
        pay_resp.raise_for_status()
    pay = pay_resp.json()
    address = pay['payment_address']
    amount_dash = pay['amount_dash']

    # 5) рисуем QR-код через Google Chart API
    qr_data = urllib.parse.quote(f"dash:{address}?amount={amount_dash}")
    qr_url = f"https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl={qr_data}"

    # 6) показываем пользователю
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text={'ru': '✅ Я оплатил', 'hy': '✅ Ես վճարել եմ', 'en': '✅ I have paid'}[lang],
            callback_data='check_payment'
        )]
    ])

    text = {
        'ru': (
            f"✅ Позиция добавлена ({qty}×{item['packaging']['volume']}).\n\n"
            f"💰 Оплатите <b>{amount_dash} DASH</b> на адрес:\n<code>{address}</code>"
        ),
        'hy': (
            f"✅ Պозиция ավելացվեց ({qty}×{item['packaging']['volume']}).\n\n"
            f"💰 Վճարեք <b>{amount_dash} DASH</b> այս հասցեին՝\n<code>{address}</code>"
        ),
        'en': (
            f"✅ Item added ({qty}×{item['packaging']['volume']}).\n\n"
            f"💰 Please pay <b>{amount_dash} DASH</b> to:\n<code>{address}</code>"
        ),
    }[lang]

    await message.answer(
        f"{text}\n\n🔗 <a href=\"{qr_url}\">Открыть QR-код для оплаты</a>",
        reply_markup=kb,
        parse_mode='HTML'
    )

    # помечаем, что ждём подтверждения платежа
    data['step'] = 'awaiting_payment'


@router.callback_query(lambda c: c.data == 'check_payment')
async def check_payment(call: types.CallbackQuery):
    chat_id = call.from_user.id
    data = user_data[chat_id]
    lang = data['lang']
    order_id = data['order_id']
    token = data['token']

    # 1) Проверяем платёж
    async with httpx.AsyncClient(
        headers={'Authorization': f'Bearer {token}'}
    ) as client:
        resp = await client.get(f"{API_V1}/payments/status/{order_id}")
        resp.raise_for_status()
    result = resp.json()['data']
    status = result['status']
    if status != 'paid':
        return await call.answer({
                                     'ru': 'Платёж не найден, попробуйте чуть позже.',
                                     'hy': 'Վճարումը չի գտնվել, նորից փորձեք:',
                                     'en': 'Payment not yet detected, please try again later.'
                                 }[lang], show_alert=True)

    # 2) Оплата есть — говорим, что получили
    await call.message.edit_text({
                                     'ru': '🎉 Оплата получена! Вот ваш клад:',
                                     'hy': '🎉 Վճարումը ստացվեց։ Ձեր կլադն է՝',
                                     'en': '🎉 Payment received! Here’s your stash:'
                                 }[lang])

    stash = result['stash']
    if not stash:
        return await call.message.answer({
                                             'ru': 'Клад ещё не загружен, подождите немного и нажмите «✅ Я оплатил» снова.',
                                             'hy': 'Կլադը դեռ պատրաստ չէ, նորից սեղմեք՝ «✅ Ես վճարել եմ».',
                                             'en': 'Your stash isn’t ready yet, please wait a bit and press “✅ I have paid” again.'
                                         }[lang])

    # 5) Отправляем фото
    photo_url = stash.get('photo_url') or stash.get('photo')
    caption = f"{stash['packaging']['volume']} — {stash['packaging']['price']}$"
    #     await call.message.answer_photo(
    #         photo=photo_url,
    #         caption={
    #             'ru':'🎁 Вот ваш клад! Сохраните это фото, оно одноразовое.',
    #             'hy':'🎁 Ահա ձեր կլադը։ Մի՛ կորցրեք լուսանկարը՝ մեկանգամյա է։',
    #             'en':'🎁 Here’s your stash! Keep this photo—it’s one-time only.'
    #         }[lang]
    #     )
    try:
        await call.message.answer_photo(
            photo=stash.get('photo_url') or stash.get('photo'),
            caption=f"{stash['packaging']['volume']} — {stash['packaging']['price']}$"
        )
    except:
        await call.message.answer(
            f"{caption}\n\n🔗 Ссылка на фото: {photo_url}"
        )

    # 6) И обратно в главное меню
    data['step'] = 'main'
    btn = {
        'ru': '🛒 Купить',
        'hy': '🛒 Գնել',
        'en': '🛒 Buy'
    }[lang]
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await call.message.answer({
                                  'ru': 'Выберите действие:',
                                  'hy': 'Ընտրեք գործողությունը:',
                                  'en': 'Choose an action:'
                              }[lang], reply_markup=kb)


@router.callback_query(lambda c: c.data and c.data.startswith('district:'))
async def on_district_selected(call: types.CallbackQuery):
    chat_id = call.from_user.id
    data = user_data[chat_id]
    lang = data['lang']
    token = data['token']
    district_id = int(call.data.split(':', 1)[1])
    data['district_id'] = district_id

    # 1) Создаём заказ
    order_payload = {
        'user_id': data['user_id'],
        'city_id': data['city_id'],
        'district_id': district_id,
        'coupon_id': data.get('coupon_id'),  # передаём купон, если есть
        'apply_subscription_discount': data.get('apply_subscription_discount', False),
    }
    async with httpx.AsyncClient(
        headers={'Authorization': f'Bearer {token}'}
    ) as client:
        resp = await client.post(f"{API_V1}/orders", json=order_payload)
        resp.raise_for_status()
    order = resp.json()['data']
    data['order_id'] = order['id']

    # 2) Запрашиваем список продуктов
    async with httpx.AsyncClient(
        headers={'Authorization': f'Bearer {token}'}
    ) as client:
        resp = await client.get(f"{API_V1}/products", params={
            'city_id': data['city_id'],
            'district_id': data['district_id'],
        })
        resp.raise_for_status()
    products = resp.json()['data']

    buttons = [
        [InlineKeyboardButton(text=p[f'name_{lang}'], callback_data=f'product:{p["id"]}')]
        for p in products
    ]
    buttons.append([InlineKeyboardButton(text={'ru': '🔙 Назад к районам', 'en': '🔙 Back'}[lang], callback_data='back_to_districts')])
    buttons.append([InlineKeyboardButton(text={'ru': '❌ Отмена', 'en': '❌ Cancel'}[lang], callback_data='back_to_main')])



    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await call.message.edit_text(
        {
            'ru': 'Выберите товар:',
            'hy': 'Ընտրեք ապրանքը:',
            'en': 'Select a product:'
        }[lang],
        reply_markup=kb
    )

    data['step'] = 'product'
    await call.answer()

@router.callback_query(lambda c: c.data == 'back_to_main')
async def back_to_main(c: types.CallbackQuery):
    uid = c.from_user.id
    user_data[uid]['step'] = 'main'
    await c.answer()
    # тут вызвать ту же функцию, что и по кнопке «📋 Меню»
    await show_main_menu(c.message)

@router.callback_query(lambda c: c.data == 'back_to_cities')
async def back_to_cities(cq: types.CallbackQuery):
    chat_id = cq.from_user.id
    data    = user_data[chat_id]
    lang    = data['lang']
    token   = data['token']

    # 1) Запрашиваем список городов
    async with httpx.AsyncClient(headers={'Authorization': f'Bearer {token}'}) as cli:
        resp = await cli.get(f"{API_V1}/cities")
        resp.raise_for_status()
    cities = resp.json().get('data', [])

    # 2) Собираем клавиатуру
    buttons = [
        [InlineKeyboardButton(text=c[f'name_{lang}'], callback_data=f"city:{c['id']}")]
        for c in cities
    ]
    buttons.append([
        InlineKeyboardButton(
            text={'ru':'❌ Отмена','hy':'❌ Չեղարկել','en':'❌ Cancel'}[lang],
            callback_data='back_to_main'
        )
    ])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    # 3) Рисуем
    await cq.message.edit_text(
        {
            'ru': '✏️ Выберите город:',
            'hy': '✏️ Ընտրեք քաղաքը՝',
            'en': '✏️ Select a city:'
        }[lang],
        reply_markup=kb
    )

    # 4) Обновляем шаг
    data['step'] = 'city'
    await cq.answer()
@router.callback_query(lambda c: c.data == 'back_to_districts')
async def back_to_districts(cq: types.CallbackQuery):
    chat_id = cq.from_user.id
    data    = user_data[chat_id]
    lang    = data['lang']
    token   = data['token']
    city_id = data.get('city_id')

    if not city_id:
        return await cq.answer("Нечего показать", show_alert=True)

    # 1) Запрашиваем районы по city_id
    async with httpx.AsyncClient(headers={'Authorization': f'Bearer {token}'}) as cli:
        resp = await cli.get(f"{API_V1}/districts", params={'city_id': city_id})
        resp.raise_for_status()
    districts = resp.json().get('data', [])

    # 2) Собираем клавиатуру
    buttons = [
        [InlineKeyboardButton(text=d[f'name_{lang}'], callback_data=f"district:{d['id']}")]
        for d in districts
    ]
    buttons.append([
        InlineKeyboardButton(
            text={'ru':'🔙 Назад к городам','hy':'🔙 Վերադարձ քաղաքներ','en':'🔙 Back to cities'}[lang],
            callback_data='back_to_cities'
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text={'ru':'❌ Отмена','hy':'❌ Չեղարկել','en':'❌ Cancel'}[lang],
            callback_data='back_to_main'
        )
    ])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    # 3) Рисуем
    await cq.message.edit_text(
        {
            'ru': '✏️ Выберите район:',
            'hy': '✏️ Ընտրեք թաղամասը՝',
            'en': '✏️ Select a district:'
        }[lang],
        reply_markup=kb
    )

    # 4) Обновляем шаг
    data['step'] = 'district'
    await cq.answer()


@router.callback_query(lambda c: c.data == 'back_to_products')
async def back_to_products(cq: types.CallbackQuery):
    chat_id = cq.from_user.id
    data    = user_data[chat_id]
    lang    = data['lang']
    token   = data['token']
    city_id     = data.get('city_id')
    district_id = data.get('district_id')

    # 1) Проверяем, что у нас есть нужные данные
    if not city_id or not district_id:
        return await cq.answer("Нечего показать", show_alert=True)

    # 2) Запрашиваем продукты
    async with httpx.AsyncClient(headers={'Authorization': f'Bearer {token}'}) as cli:
        resp = await cli.get(f"{API_V1}/products", params={
            'city_id':     city_id,
            'district_id': district_id,
        })
        resp.raise_for_status()
    products = resp.json().get('data', [])

    # 3) Собираем клавиатуру
    buttons = [
        [InlineKeyboardButton(text=p[f'name_{lang}'], callback_data=f'product:{p["id"]}')]
        for p in products
    ]
    buttons.append([
        InlineKeyboardButton(
            text={'ru':'🔙 Назад к районам','hy':'🔙 Վերադարձ թաղամասեր','en':'🔙 Back to districts'}[lang],
            callback_data='back_to_districts'
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text={'ru':'❌ Отмена','hy':'❌ Չեղարկել','en':'❌ Cancel'}[lang],
            callback_data='back_to_main'
        )
    ])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    # 4) Рисуем сообщение заново
    await cq.message.edit_text(
        {
            'ru':'✏️ Выберите товар:',
            'hy':'✏️ Ընտրեք ապրանքը՝',
            'en':'✏️ Select a product:'
        }[lang],
        reply_markup=kb
    )

    # 5) Меняем step
    data['step'] = 'product'
    await cq.answer()
