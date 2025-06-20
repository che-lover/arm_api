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


class FinanceStates(StatesGroup):
    choose_action        = State()
    send_enter_address   = State()
    send_enter_amount    = State()
    send_confirm         = State()


async def show_finances_menu(msg: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Баланс",          callback_data="fn_balance")
    builder.button(text="📤 Отправить DASH",  callback_data="fn_send")
    builder.button(text="↩️ Назад",           callback_data="back_to_main")
    builder.adjust(2)
    await msg.edit_text(
        "💰 *Финансы* — выберите действие:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


# — Входим в «Финансы» из главного меню
@router.callback_query(
    AuthStates.authenticated,
    StateFilter(MainStates.choosing_scenario),
    lambda c: c.data == "sc_finances"
)
async def enter_finances(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(FinanceStates.choose_action)
    await show_finances_menu(cq.message, state)

@router.callback_query(FinanceStates.choose_action, lambda c: c.data == "fn_balance")
async def fn_balance(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as cli:
        resp = await cli.get(f"{API_V1}/payments/balance")
    if resp.status_code == 200:
        balance = resp.json().get("balance")
        await cq.message.answer(f"💰 Текущий баланс: *{balance}* DASH", parse_mode="Markdown")
    else:
        await cq.message.answer("❌ Ошибка при получении баланса.")
    # обратно в меню «Финансы»
    await show_finances_menu(cq.message, state)


# — Начало «Отправить DASH»
@router.callback_query(FinanceStates.choose_action, lambda c: c.data == "fn_send")
async def fn_send_start(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(FinanceStates.send_enter_address)

    # сразу даём кнопку «Назад»
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Назад", callback_data="fn_back_to_finances")
    builder.adjust(1)

    await cq.message.edit_text(
        "📤 Введите *адрес* для отправки DASH:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


# — «Назад» из этапов адрес/сумма
@router.callback_query(
    StateFilter(FinanceStates.send_enter_address, FinanceStates.send_enter_amount),
    lambda c: c.data == "fn_back_to_finances"
)
async def fn_back_from_send(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(FinanceStates.choose_action)
    await show_finances_menu(cq.message, state)


@router.message(FinanceStates.send_enter_address)
async def fn_send_address(msg: types.Message, state: FSMContext):
    address = msg.text.strip()
    await state.update_data(to_address=address)
    await state.set_state(FinanceStates.send_enter_amount)

    # тоже даём кнопку «Назад»
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Назад", callback_data="fn_back_to_finances")
    builder.adjust(1)

    await msg.answer(
        "💵 Теперь введите сумму DASH для отправки (например: 0.5):",
        reply_markup=builder.as_markup()
    )


@router.message(FinanceStates.send_enter_amount)
async def fn_send_amount(msg: types.Message, state: FSMContext):
    text = msg.text.strip()
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except:
        return await msg.answer("❌ Неверный формат суммы. Введите число > 0.")

    await state.update_data(amount_dash=amount)

    data    = await state.get_data()
    address = data["to_address"]

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="fn_confirm_send")
    builder.button(text="❌ Отменить",    callback_data="fn_cancel_send")
    builder.adjust(2)

    await msg.answer(
        f"📤 Подтвердить отправку *{amount}* DASH на адрес:\n`{address}`?",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(FinanceStates.send_confirm)


@router.callback_query(FinanceStates.send_confirm, lambda c: c.data == "fn_confirm_send")
async def fn_confirm_send(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data    = await state.get_data()
    address = data["to_address"]
    amount  = data["amount_dash"]
    token   = data["token"]

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as cli:
        resp = await cli.post(
            f"{API_V1}/payments/send",
            json={"to_address": address, "amount_dash": amount}
        )
    if resp.status_code == 200:
        txid = resp.json().get("txid")
        await cq.message.answer(
            f"✅ Отправлено *{amount}* DASH на `{address}`\nTxID: `{txid}`",
            parse_mode="Markdown"
        )
    else:
        err = resp.json().get("error") or ""
        await cq.message.answer(f"❌ Ошибка отправки DASH. {err}")

    # обратно в меню «Финансы»
    await state.set_state(FinanceStates.choose_action)
    await show_finances_menu(cq.message, state)


@router.callback_query(FinanceStates.send_confirm, lambda c: c.data == "fn_cancel_send")
async def fn_cancel_send(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Отправка отменена", show_alert=True)
    await state.set_state(FinanceStates.choose_action)
    await show_finances_menu(cq.message, state)


# — «↩️ Назад» из меню «Финансы»
@router.callback_query(FinanceStates.choose_action, lambda c: c.data == "back_to_main")
async def fn_back_to_main(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    from admin.handlers.menu import cmd_menu
    await state.set_state(MainStates.choosing_scenario)
    await cmd_menu(cq.message, state)
