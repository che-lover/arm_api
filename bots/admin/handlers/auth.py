import os, logging, httpx
from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

API_AUTH = os.getenv('API_BASE_URL').rstrip('/') + '/v1/auth'

class AuthStates(StatesGroup):
    authenticated = State()

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в админ-панель!\n"
        "Введите /login для входа."
    )

@router.message(Command("login"))
async def cmd_login(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    logging.info("AUTH: login handler for %s", telegram_id)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_AUTH}/bot-login",
            json={'telegram_id': telegram_id}
        )

    if resp.status_code == 200 and (d := resp.json().get('data')):
        user, token = d['user'], d['token']
        role = user['role']['name']
        if user['role_id'] not in (1,2,3,4):
            return await message.answer("❌ У вас нет прав администратора.")
        await state.update_data(token=token, role=role)
        await state.set_state(AuthStates.authenticated)
        await message.answer("✅ Успешно! Введите /menu для перехода в панель.")
    else:
        await message.answer("❌ Ошибка входа, попробуйте снова.")

@router.message(AuthStates.authenticated, Command("logout"))
async def cmd_logout(message: types.Message, state: FSMContext):
    data = await state.get_data()
    token = data.get('token')
    if not token:
        return await message.answer("⚠️ Вы не в системе.")
    async with httpx.AsyncClient(headers={'Authorization':f'Bearer {token}'}) as client:
        await client.post(f"{API_AUTH}/bot-logout")
    await state.clear()
    await message.answer("🔒 Вы вышли из админ-панели.")
