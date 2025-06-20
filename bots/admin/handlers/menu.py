import os
import httpx

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from admin.handlers.auth import AuthStates
from admin.handlers.common_states import MainStates
from admin.handlers.coupons import show_coupons_menu, CouponStates
from admin.handlers.finances import show_finances_menu, FinanceStates
from admin.handlers.locations import LocationsStates, show_locations_menu
from admin.handlers.roles import RolesStates, enter_add_admin, enter_set_role
from admin.handlers.settings import show_settings_menu, SettingsStates
from admin.handlers.showcase import ShowcaseStates, show_showcase_menu

API_V1 = os.getenv("API_BASE_URL").rstrip("/") + "/v1"



router = Router()

@router.message(AuthStates.authenticated, Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data["role"]

    builder = InlineKeyboardBuilder()
    if role == "courier":
        builder.button(text="🛍 Витрина", callback_data="sc_showcase")
    else:
        builder.button(text="🛍 Витрина",       callback_data="sc_showcase")
        builder.button(text="📍 Локации",       callback_data="sc_locations")
        builder.button(text="🎟 Купоны",        callback_data="sc_coupons")
        builder.button(text="⚙️ Настройки",      callback_data="sc_settings")
        builder.button(text="📊 Статистика",    callback_data="sc_stats")
        builder.button(text="💰 Финансы",       callback_data="sc_finances")
        builder.button(text="✉️ Рассылки",      callback_data="sc_mailings")
        builder.button(text="🌐 Язык",           callback_data="sc_language")
        if role == "supervisor":
            builder.button(text="👑 Назначить админа", callback_data="add_admin")
        if role in ("supervisor","admin"):
            builder.button(text="🔄 Сменить роль",    callback_data="set_role")
            builder.button(text="Команда",    callback_data="team")
    builder.button(text="🚪 Выход", callback_data="logout")

    builder.adjust(2)
    await state.set_state(MainStates.choosing_scenario)
    await message.answer("🔧 Выберите раздел:", reply_markup=builder.as_markup())

@router.callback_query(MainStates.choosing_scenario, lambda c: c.data == "team")
async def show_team(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token = (await state.get_data())["token"]

    # забираем всех пользователей
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as cli:
        resp = await cli.get(f"{API_V1}/users")
    if resp.status_code != 200:
        await cq.message.answer("❌ Не удалось получить список пользователей.")
        return

    users = resp.json().get("data", [])
    # оставляем только роли с id 1–4
    team = [
        u for u in users
        if u.get("role_id") in (1, 2, 3, 4)
    ]

    # формируем строки вида "@username — admin"
    lines = []
    for u in team:
        uname = u.get("telegram_username")
        mention = f"@{uname}" if uname else str(u["telegram_id"])
        role_name = u["role"]["name"]
        # показываем supervisor как admin
        display_role = "admin" if role_name == "supervisor" else role_name
        lines.append(f"{mention} — {display_role}")

    text = "— нет никого —" if not lines else "\n".join(lines)
    await cq.message.answer(f"👥 *Команда:*\n{text}", parse_mode="Markdown")
    # возвращаем пользователя в главное меню
    await cmd_menu(cq.message, state)

@router.callback_query(MainStates.choosing_scenario)
async def choose_scenario(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    key = cq.data

    # # КУРЬЕР: только клад
    # if key == "inv_add":
    #     await state.set_state(InventoryStates.add_inventory)
    #     await start_add_inventory(cq.message)
    #     return
    # if key == "inv_confirm":
    #     await state.set_state(InventoryStates.confirm_inventory)
    #     await start_confirm_inventory(cq.message)
    #     return
    # if key == "inv_reject":
    #     await state.set_state(InventoryStates.reject_inventory)
    #     await start_reject_inventory(cq.message)
    #     return

    # АДМИН и МЕНЕДЖЕР: полные сценарии
    match key:
        case "sc_showcase":
            await state.set_state(ShowcaseStates.choose_action)
            await show_showcase_menu(cq.message, state)

        case "sc_locations":
            await state.set_state(LocationsStates.choose_action)
            await show_locations_menu(cq.message, state)

        case "sc_coupons":
            await state.set_state(CouponStates.choose_action)
            await show_coupons_menu(cq.message, state)

        case "sc_settings":
            await state.set_state(SettingsStates.choose_action)
            await show_settings_menu(cq.message, state)
        #
        # case "sc_stats":
        #     await state.set_state(StatsStates.choose_action)
        #     await show_stats_menu(cq.message)
        #
        case "sc_finances":
            await state.set_state(FinanceStates.choose_action)
            await show_finances_menu(cq.message, state)
        #
        # case "sc_mailings":
        #     await state.set_state(MailingsStates.choose_action)
        #     await show_mailings_menu(cq.message)
        #
        # case "sc_language":
        #     await state.set_state(LanguageStates.choose_action)
        #     await show_language_menu(cq.message)
        #
        case "add_admin":
            await enter_add_admin(cq, state)
            return
        #
        case "set_role":
            # await state.set_state(RolesStates.set_role)
            await enter_set_role(cq, state)
            return

        case "logout":
            await state.clear()
            await cq.message.edit_text("🔒 Вы вышли из админ-панели.")

        case _:
            # Игнорируем всё остальное или возвращаемся в меню
            await cmd_menu(cq.message, state)
