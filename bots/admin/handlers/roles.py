import html
import os
import httpx
from datetime import datetime, timedelta

from aiogram import Router, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin.handlers.auth import AuthStates
from admin.handlers.common_states import MainStates

API_V1 = os.getenv("API_BASE_URL").rstrip("/") + "/v1"

router = Router()


class RolesStates(StatesGroup):
    # выдать админку
    add_admin = State()
    confirm_add_admin = State()
    # отозвать админку
    remove_admin = State()
    confirm_remove_admin = State()

    set_user = State()
    set_role_choose = State()
    confirm_set_role = State()


# ——— старт выдачи админки ———
@router.callback_query(
    AuthStates.authenticated,
    StateFilter(MainStates.choosing_scenario),
    lambda c: c.data == "add_admin"
)
async def enter_add_admin(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(RolesStates.add_admin)
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="roles_cancel")
    kb.adjust(1)
    await cq.message.edit_text(
        "👑 Введите *Telegram-ID* пользователя, "
        "которому вы хотите выдать права admin:",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )


@router.message(RolesStates.add_admin)
async def process_add_admin_id(msg: types.Message, state: FSMContext):
    text = msg.text.strip()
    if not text.isdigit():
        return await msg.answer("❌ ID должен состоять только из цифр.")
    telegram_id = int(text)

    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.get(f"{API_V1}/users", params={"telegram_id": telegram_id})
    if resp.status_code != 200:
        return await msg.answer("❌ Не удалось получить список пользователей.")

    users = resp.json().get("data", [])
    user = next((u for u in users if u.get("telegram_id") == telegram_id), None)
    if not user:
        return await msg.answer("❌ Пользователь с таким Telegram-ID не найден. Попробуйте ещё раз.")

    # сохраняем пользователя в state
    await state.update_data(target_user=user)

    # спрашиваем подтверждение
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Назначить", callback_data="roles_confirm_add")
    builder.button(text="❌ Отмена",    callback_data="roles_cancel_add")
    builder.adjust(2)
    name = html.escape(user.get('name') or str(telegram_id))
    role = html.escape(user['role']['name'])

    await msg.answer(
        f"Пользователь <b>{name}</b> "
        f"(telegram_id <code>{telegram_id}</code>)\n"
        f"текущая роль: <code>{role}</code>\n\n"
        "Выдать ему права admin?",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )

    await state.set_state(RolesStates.confirm_add_admin)


@router.callback_query(RolesStates.confirm_add_admin, lambda c: c.data == "roles_confirm_add")
async def sc_confirm_add(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data = await state.get_data()
    user = data["target_user"]
    user_id = user["id"]
    token = data["token"]

    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.post(f"{API_V1}/users/{user_id}/assign-admin")

    if resp.status_code in (200, 201):
        await cq.message.answer("✅ Пользователь успешно назначен администратором!")
    else:
        await cq.message.answer("❌ Не удалось назначить admin. Попробуйте позже.")

    # обратно в главное меню
    await state.set_state(MainStates.choosing_scenario)
    from admin.handlers.menu import cmd_menu
    await cmd_menu(cq.message, state)


@router.callback_query(RolesStates.confirm_add_admin, lambda c: c.data == "roles_cancel_add")
async def sc_cancel_add(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Операция отменена", show_alert=True)
    # назад в главное меню
    await state.set_state(MainStates.choosing_scenario)
    from admin.handlers.menu import cmd_menu
    await cmd_menu(cq.message, state)


# ——— старт отзыва админки ———
@router.callback_query(
    AuthStates.authenticated,
    StateFilter(MainStates.choosing_scenario),
    lambda c: c.data == "set_role"
)
async def enter_remove_admin(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(RolesStates.remove_admin)
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="roles_cancel")
    kb.adjust(1)
    await cq.message.edit_text(
        "🔄 Введите *Telegram-ID* пользователя, "
        "чьи права admin нужно отозвать:",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )


@router.message(RolesStates.remove_admin)
async def process_remove_admin_id(msg: types.Message, state: FSMContext):
    text = msg.text.strip()
    if not text.isdigit():
        return await msg.answer("❌ ID должен состоять только из цифр.")
    telegram_id = int(text)

    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.get(f"{API_V1}/users")
    if resp.status_code != 200:
        return await msg.answer("❌ Не удалось получить список пользователей.")

    users = resp.json().get("data", [])
    user = next((u for u in users if u.get("telegram_id") == telegram_id), None)
    if not user:
        return await msg.answer("❌ Пользователь с таким Telegram-ID не найден. Попробуйте ещё раз.")

    await state.update_data(target_user=user)

    # подтверждение
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Отозвать admin", callback_data="roles_confirm_remove")
    builder.button(text="❌ Отмена",         callback_data="roles_cancel_remove")
    builder.adjust(2)

    await msg.answer(
        f"Пользователь *{user.get('name') or telegram_id}*\n"
        f"текущая роль: `{user['role']['name']}`\n\n"
        "Отозвать у него права admin?",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(RolesStates.confirm_remove_admin)


@router.callback_query(RolesStates.confirm_remove_admin, lambda c: c.data == "roles_confirm_remove")
async def sc_confirm_remove(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data = await state.get_data()
    user = data["target_user"]
    user_id = user["id"]
    token = data["token"]

    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.post(f"{API_V1}/users/{user_id}/revoke-admin")

    if resp.status_code in (200, 204):
        await cq.message.answer("✅ Права admin успешно отозваны.")
    else:
        await cq.message.answer("❌ Не удалось отозвать admin. Попробуйте позже.")

    await state.set_state(MainStates.choosing_scenario)
    from admin.handlers.menu import cmd_menu
    await cmd_menu(cq.message, state)


@router.callback_query(RolesStates.confirm_remove_admin, lambda c: c.data == "roles_cancel_remove")
async def sc_cancel_remove(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Операция отменена", show_alert=True)
    await state.set_state(MainStates.choosing_scenario)
    from admin.handlers.menu import cmd_menu
    await cmd_menu(cq.message, state)

# 1) Входим в «Сменить роль» из главного меню
@router.callback_query(
    AuthStates.authenticated,
    StateFilter(MainStates.choosing_scenario),
    lambda c: c.data == "set_role"
)
async def enter_set_role(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(RolesStates.set_user)
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="roles_cancel")
    kb.adjust(1)
    await cq.message.edit_text(
        "🔄 Введите *Telegram-ID* пользователя, "
        "чью роль вы хотите изменить:",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )


# 2) Читаем ID и запрашиваем список всех юзеров
@router.message(RolesStates.set_user)
async def process_set_user(msg: types.Message, state: FSMContext):
    text = msg.text.strip()
    if not text.isdigit():
        return await msg.answer("❌ ID должен состоять только из цифр.")
    tg_id = int(text)

    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.get(f"{API_V1}/users")
    if resp.status_code != 200:
        return await msg.answer("❌ Не удалось получить список пользователей.")

    users = resp.json().get("data", [])
    user = next((u for u in users if u.get("telegram_id") == tg_id), None)
    if not user:
        return await msg.answer("❌ Пользователь с таким Telegram-ID не найден.")

    await state.update_data(target_user=user)

    # 3) Предлагаем список ролей
    ROLES = [
        ("client",   5),
        ("courier",  4),
        ("manager",  3),
        ("admin",    2),
    ]
    builder = InlineKeyboardBuilder()
    for name, rid in ROLES:
        builder.button(text=name, callback_data=f"sr_{rid}")
    builder.button(text="❌ Отмена", callback_data="sr_cancel")
    builder.adjust(2)

    await msg.answer(
        f"👤 Вы изменяете *{user.get('name') or user['telegram_id']}*\n"
        f"текущая роль: `{user['role']['name']}`\n\n"
        "Выберите новую роль:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(RolesStates.set_role_choose)


# 4) Пользователь выбирает новую роль
@router.callback_query(RolesStates.set_role_choose, lambda c: c.data.startswith("sr_"))
async def choose_new_role(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    rid = int(cq.data.split("_", 1)[1])
    await state.update_data(new_role_id=rid)
    data = await state.get_data()
    user = data["target_user"]

    # спрашиваем подтверждение
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="sr_confirm")
    builder.button(text="❌ Отмена",     callback_data="sr_cancel")
    builder.adjust(2)

    await cq.message.answer(
        f"👤 *{user.get('name') or user['telegram_id']}*\n"
        f"сменить роль с `{user['role']['name']}` на `{rid}`?",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(RolesStates.confirm_set_role)


# 5a) Подтверждаем смену
@router.callback_query(RolesStates.confirm_set_role, lambda c: c.data == "sr_confirm")
async def sc_confirm_set(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data = await state.get_data()
    user = data["target_user"]
    rid  = data["new_role_id"]
    token = data["token"]

    # в зависимости от роли используем разные endpoint’ы
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        if rid == 4:
            # admin
            resp = await cli.post(f"{API_V1}/users/{user['id']}/assign-admin")
        elif rid == 1:
            # обратно в client
            resp = await cli.post(f"{API_V1}/users/{user['id']}/revoke-admin")
        else:
            # для courier/manager — generic update
            resp = await cli.put(
                f"{API_V1}/users/{user['id']}",
                json={"role_id": rid}
            )

    if resp.status_code in (200, 201, 204):
        await cq.message.answer("✅ Роль успешно изменена.")
    else:
        await cq.message.answer("❌ Ошибка при смене роли.")

    # обратно в главное меню
    await state.set_state(MainStates.choosing_scenario)
    from admin.handlers.menu import cmd_menu
    await cmd_menu(cq.message, state)

# 5b) Отмена на любом этапе
@router.callback_query(
    RolesStates.set_role_choose, lambda c: c.data == "sr_cancel"
)
@router.callback_query(
    RolesStates.confirm_set_role, lambda c: c.data == "sr_cancel"
)
async def sc_cancel_set(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Операция отменена", show_alert=True)
    # возвращаем в главное меню
    await state.set_state(MainStates.choosing_scenario)
    from admin.handlers.menu import cmd_menu
    await cmd_menu(cq.message, state)

@router.callback_query(lambda c: c.data=="roles_cancel", StateFilter(*RolesStates))
async def roles_cancel(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Операция отменена", show_alert=True)
    # возвращаемся в главное меню бота
    await state.set_state(MainStates.choosing_scenario)
    from admin.handlers.menu import cmd_menu
    await cmd_menu(cq.message, state)
