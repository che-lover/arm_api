import os
import httpx

from aiogram import Router, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin.handlers.auth import AuthStates
from admin.handlers.common_states import MainStates

API_V1 = os.getenv("API_BASE_URL").rstrip("/") + "/v1"

router = Router()


class SettingsStates(StatesGroup):
    choose_action         = State()
    change_exchange_url   = State()
    change_channel_link   = State()
    change_operator       = State()


async def show_settings_menu(msg: types.Message, state: FSMContext):
    token = (await state.get_data())["token"]
    # получаем текущие значения
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as cli:
        resp = await cli.get(f"{API_V1}/settings/bot")
    cfg = resp.json().get("data", {}) if resp.status_code == 200 else {}

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"🔗 Обменник: {cfg.get('exchange_url') or '—'}",
        callback_data="st_exchange_url",
    )
    builder.button(
        text=f"🛡️ Капча: {'ON' if cfg.get('captcha_enabled') else 'OFF'}",
        callback_data="st_captcha",
    )
    builder.button(
        text=f"📣 Канал: {cfg.get('channel_link') or '—'}",
        callback_data="st_channel",
    )
    builder.button(
        text=f"📞 Оператор: {cfg.get('operator_contact') or '—'}",
        callback_data="st_operator",
    )
    builder.button(text="↩️ Назад", callback_data="back_to_main")
    builder.adjust(2)

    await msg.edit_text(
        "⚙️ *Настройки бота* — выберите параметр для изменения:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup(),
    )


# 1) Вход из главного меню
@router.callback_query(
    AuthStates.authenticated,
    StateFilter(MainStates.choosing_scenario),
    lambda c: c.data == "sc_settings"
)
async def enter_settings(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(SettingsStates.choose_action)
    await show_settings_menu(cq.message, state)


# 2) «↩️ Назад» в главное меню из настроек
@router.callback_query(SettingsStates.choose_action, lambda c: c.data == "back_to_main")
async def settings_back_to_main(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(MainStates.choosing_scenario)
    from admin.handlers.menu import cmd_menu
    await cmd_menu(cq.message, state)


# 3) «↩️ Назад» из любого под-состояния настроек
_SUBSTATES = [
    SettingsStates.change_exchange_url,
    SettingsStates.change_channel_link,
    SettingsStates.change_operator,
]
@router.callback_query(StateFilter(*_SUBSTATES), lambda c: c.data == "st_back")
async def settings_back_to_menu(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(SettingsStates.choose_action)
    await show_settings_menu(cq.message, state)


# 4) Изменить URL обменника
@router.callback_query(SettingsStates.choose_action, lambda c: c.data == "st_exchange_url")
async def settings_start_exchange(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(SettingsStates.change_exchange_url)
    kb = InlineKeyboardBuilder().button(text="↩️ Назад", callback_data="st_back").as_markup()
    await cq.message.edit_text("🔗 Введите новый URL обменника:", reply_markup=kb)

@router.message(SettingsStates.change_exchange_url)
async def settings_change_exchange(msg: types.Message, state: FSMContext):
    url = msg.text.strip()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as cli:
        resp = await cli.put(f"{API_V1}/settings/bot", json={"exchange_url": url})
    if resp.status_code == 200:
        await msg.answer("✅ URL обменника обновлён.")
    else:
        await msg.answer("❌ Не удалось сохранить URL.")
    await state.set_state(SettingsStates.choose_action)
    await show_settings_menu(msg, state)


# 5) Переключить капчу
@router.callback_query(SettingsStates.choose_action, lambda c: c.data == "st_captcha")
async def settings_toggle_captcha(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as cli:
        cur = (await cli.get(f"{API_V1}/settings/bot")).json().get("data", {})
        new = not cur.get("captcha_enabled", True)
        resp = await cli.put(f"{API_V1}/settings/bot", json={"captcha_enabled": new})
    if resp.status_code == 200:
        await cq.message.answer(f"🛡️ Капча теперь {'включена' if new else 'выключена'}.")
    else:
        await cq.message.answer("❌ Не удалось переключить капчу.")
    await state.set_state(SettingsStates.choose_action)
    await show_settings_menu(cq.message, state)


# 6) Изменить ссылку на канал
@router.callback_query(SettingsStates.choose_action, lambda c: c.data == "st_channel")
async def settings_start_channel(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(SettingsStates.change_channel_link)
    kb = InlineKeyboardBuilder().button(text="↩️ Назад", callback_data="st_back").as_markup()
    await cq.message.edit_text("📣 Введите новый URL вашего канала:", reply_markup=kb)

@router.message(SettingsStates.change_channel_link)
async def settings_change_channel(msg: types.Message, state: FSMContext):
    link = msg.text.strip()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as cli:
        resp = await cli.put(f"{API_V1}/settings/bot", json={"channel_link": link})
    if resp.status_code == 200:
        await msg.answer("✅ Ссылка на канал обновлена.")
    else:
        await msg.answer("❌ Не удалось сохранить ссылку.")
    await state.set_state(SettingsStates.choose_action)
    await show_settings_menu(msg, state)


# 7) Изменить контакт оператора
@router.callback_query(SettingsStates.choose_action, lambda c: c.data == "st_operator")
async def settings_start_operator(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(SettingsStates.change_operator)
    kb = InlineKeyboardBuilder().button(text="↩️ Назад", callback_data="st_back").as_markup()
    await cq.message.edit_text("📞 Введите контакт оператора:", reply_markup=kb)

@router.message(SettingsStates.change_operator)
async def settings_change_operator(msg: types.Message, state: FSMContext):
    contact = msg.text.strip()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as cli:
        resp = await cli.put(f"{API_V1}/settings/bot", json={"operator_contact": contact})
    if resp.status_code == 200:
        await msg.answer("✅ Контакт оператора обновлён.")
    else:
        await msg.answer("❌ Не удалось сохранить контакт.")
    await state.set_state(SettingsStates.choose_action)
    await show_settings_menu(msg, state)


# 8) Фоллбэк для любых текстовых сообщений в меню настроек
@router.message(SettingsStates.choose_action)
async def settings_fallback_text(msg: types.Message, state: FSMContext):
    await msg.answer("❌ Пожалуйста, используйте кнопки меню или нажмите ↩️ Назад.")


# 9) Фоллбэк для любых некорректных callback в меню настроек
@router.callback_query(SettingsStates.choose_action)
async def settings_fallback_callback(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await show_settings_menu(cq.message, state)
