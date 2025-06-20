# admin/handlers/coupons.py

import os
import httpx
from aiogram import Router, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin.handlers.auth import AuthStates
from admin.handlers.common_states import MainStates

API_V1 = os.getenv("API_BASE_URL").rstrip("/") + "/v1"

router = Router()


class CouponStates(StatesGroup):
    choose_action   = State()
    create_code     = State()
    create_discount = State()
    create_expires  = State()


async def show_coupons_menu(msg: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="🎫 Активные купоны", callback_data="cp_active")
    builder.button(text="❌ Использованные",  callback_data="cp_used")
    builder.button(text="➕ Новый купон",       callback_data="cp_create")
    builder.button(text="↩️ Назад",             callback_data="back_to_main")
    builder.adjust(2)
    await msg.edit_text(
        "🎟 *Управление купонами* — выберите действие:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


# — вход из главного меню
@router.callback_query(
    AuthStates.authenticated,
    StateFilter(MainStates.choosing_scenario),
    lambda c: c.data == "sc_coupons"
)
async def enter_coupons(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(CouponStates.choose_action)
    await show_coupons_menu(cq.message, state)


# — показать активные
@router.callback_query(CouponStates.choose_action, lambda c: c.data=="cp_active")
async def list_active(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.get(f"{API_V1}/coupons")
    if resp.status_code==200:
        active = [c for c in resp.json().get("data",[]) if not c.get("used")]
        if not active:
            text = "— нет активных купонов —"
        else:
            text = "\n".join(
                f"#{c['id']}: `{c['code']}` — скидка {c['discount_amount']}%"
                + (f", истекает {c['expires_at']}" if c.get("expires_at") else "")
                for c in active
            )
        await cq.message.answer(f"🎫 *Активные купоны:*\n{text}", parse_mode="Markdown")
    else:
        await cq.message.answer("❌ Ошибка при получении купонов.")
    await show_coupons_menu(cq.message, state)


# — показать использованные
@router.callback_query(CouponStates.choose_action, lambda c: c.data=="cp_used")
async def list_used(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.get(f"{API_V1}/coupons")
    if resp.status_code==200:
        used = [c for c in resp.json().get("data",[]) if c.get("used")]
        if not used:
            text = "— нет использованных купонов —"
        else:
            text = "\n".join(
                f"#{c['id']}: `{c['code']}` — скидка {c['discount_amount']}%"
                for c in used
            )
        await cq.message.answer(f"❌ *Использованные купоны:*\n{text}", parse_mode="Markdown")
    else:
        await cq.message.answer("❌ Ошибка при получении купонов.")
    await show_coupons_menu(cq.message, state)


# — начать создание
@router.callback_query(CouponStates.choose_action, lambda c: c.data=="cp_create")
async def start_create(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(CouponStates.create_code)

    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ Отмена", callback_data="cp_cancel")
    kb.adjust(1)

    await cq.message.edit_text(
        "➕ Введите *код* нового купона (строка):",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )


# — получаем код
@router.message(CouponStates.create_code)
async def process_code(msg: types.Message, state: FSMContext):
    code = msg.text.strip()
    if not code:
        return await msg.answer("❌ Код не может быть пустым.")
    await state.update_data(code=code)
    await state.set_state(CouponStates.create_discount)
    await msg.answer("💵 Введите *размер скидки* в процентах (целое число от 0 до 100):", parse_mode="Markdown")

@router.callback_query(CouponStates.create_code, lambda c: c.data=="cp_cancel")
@router.callback_query(CouponStates.create_discount, lambda c: c.data=="cp_cancel")
@router.callback_query(CouponStates.create_expires, lambda c: c.data=="cp_cancel")
async def cancel_create(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(CouponStates.choose_action)
    await show_coupons_menu(cq.message, state)

# — получаем скидку
@router.message(CouponStates.create_discount)
async def process_discount(msg: types.Message, state: FSMContext):
    disc = msg.text.strip()
    if not disc.isdigit() or not (0 <= int(disc) <= 100):
        return await msg.answer("❌ Скидка должна быть числом от 0 до 100.\n💵 Введите **целое** число от 0 до 100:")
    await state.update_data(discount_amount=int(disc))
    await state.set_state(CouponStates.create_expires)
    await msg.answer("⏳ Через сколько *дней* истекает купон? Введите число или `0` для без срока:", parse_mode="Markdown")


# — получаем expires_at
@router.message(CouponStates.create_expires)
async def process_expires(msg: types.Message, state: FSMContext):
    text = msg.text.strip()
    if not text.isdigit():
        return await msg.answer("❌ Должно быть числом дней (например: `7`).")
    days = int(text)
    data = await state.get_data()
    payload = {
        "code":            data["code"],
        "discount_amount": data["discount_amount"],
        "used":            False
    }
    if days > 0:
        # рассчитываем expires_at в формате YYYY-MM-DD
        from datetime import datetime, timedelta
        expires = (datetime.utcnow() + timedelta(days=days)).date().isoformat()
        payload["expires_at"] = expires

    token = data["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.post(f"{API_V1}/coupons", json=payload)

    if resp.status_code in (200, 201):
        c = resp.json().get("data")
        await msg.answer(
            f"✅ Купон создан:\n"
            f"#{c['id']}: `{c['code']}` — скидка {c['discount_amount']}%\n"
            + (f"📅 истекает {c['expires_at']}" if c.get("expires_at") else "")
        , parse_mode="Markdown")
    else:
        await msg.answer("❌ Ошибка при создании купона.")

    # обратно в меню
    await state.set_state(CouponStates.choose_action)
    await show_coupons_menu(msg, state)


# — «↩️ Назад» из меню купонов
@router.callback_query(CouponStates.choose_action, lambda c: c.data=="back_to_main")
async def back_to_main(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    from admin.handlers.menu import cmd_menu
    await state.set_state(MainStates.choosing_scenario)
    await cmd_menu(cq.message, state)
