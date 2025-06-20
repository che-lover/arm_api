# admin/handlers/cities.py
import os
import httpx
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from admin.handlers.auth import AuthStates
from admin.filters.role_filter import RoleFilter

API_V1 = os.getenv('API_BASE_URL').rstrip('/') + '/v1'

router = Router()


class CityStates(StatesGroup):
    waiting_for_city_data = State()
    waiting_for_delete_id = State()


@router.message(AuthStates.authenticated, Command("list_cities"))
async def list_cities(message: types.Message, state: FSMContext):
    """GET /v1/cities — любой авторизованный"""
    data = await state.get_data()
    token = data["token"]
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.get(f"{API_V1}/cities")
    if resp.status_code == 200:
        payload = resp.json()
        # Laravel paginate: payload["data"] — массив городов
        cities = payload.get("data") or payload.get("data", [])
        lines = [f"{c['id']} — {c.get('name_ru') or c.get('name')}" for c in cities]
        await message.answer("🏙 Список городов:\n" + "\n".join(lines))
    else:
        await message.answer("❌ Не удалось получить список городов.")


@router.message(
    AuthStates.authenticated,
    RoleFilter(allowed=("supervisor","manager","admin")),
    Command("add_city"),
)
async def add_city_start(message: types.Message, state: FSMContext):
    await state.set_state(CityStates.waiting_for_city_data)
    await message.answer(
        "✏️ Введите новый город в формате:\n"
        "`Название_ru | Название_en | Название_hy`",
        parse_mode="Markdown",
    )


@router.message(AuthStates.authenticated, CityStates.waiting_for_city_data)
async def add_city_done(message: types.Message, state: FSMContext):
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 3:
        return await message.answer(
            "❌ Неверный формат. Пример:\n"
            "`Москва | Moscow | Մոսկվա`",
            parse_mode="Markdown",
        )

    name_ru, name_en, name_hy = parts
    data = {
        "name_ru": name_ru,
        "name_en": name_en,
        "name_hy": name_hy,
        "name": name_ru,
    }
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.post(f"{API_V1}/cities", json=data)

    if resp.status_code in (200, 201):
        city = resp.json().get("city")
        await message.answer(f"✅ Город создан: {city['id']} — {city['name_ru']}")
    else:
        await message.answer("❌ Не удалось создать город.")

    await state.reset_state(with_data=False)


@router.message(
    AuthStates.authenticated,
    RoleFilter(allowed=("supervisor","manager","admin")),
    Command("delete_city"),
)
async def delete_city_start(message: types.Message, state: FSMContext):
    await state.set_state(CityStates.waiting_for_delete_id)
    await message.answer("🗑 Введите ID города для удаления:")


@router.message(AuthStates.authenticated, CityStates.waiting_for_delete_id)
async def delete_city_done(message: types.Message, state: FSMContext):
    city_id = message.text.strip()
    if not city_id.isdigit():
        return await message.answer("❌ ID должен быть числом.")

    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.delete(f"{API_V1}/cities/{city_id}")

    if resp.status_code in (204, 200):
        await message.answer(f"✅ Город {city_id} удалён.")
    else:
        await message.answer("❌ Не удалось удалить город.")

    await state.reset_state(with_data=False)
