# admin/handlers/districts.py
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


class DistrictStates(StatesGroup):
    waiting_for_district_data = State()
    waiting_for_delete_id     = State()


@router.message(AuthStates.authenticated, Command("list_districts"))
async def list_districts(message: types.Message, state: FSMContext):
    """GET /v1/districts — любой авторизованный"""
    data = await state.get_data()
    token = data["token"]

    # можно добавить фильтр ?city_id=…
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.get(f"{API_V1}/districts")
    if resp.status_code == 200:
        payload = resp.json()
        districts = payload.get("data") or payload.get("data", [])
        lines = [f"({d['city']['name_ru']}{d['id']} — {d.get('name_ru') or d.get('name')}" for d in districts]
        await message.answer("🏘 Список районов:\n" + "\n".join(lines))
    else:
        await message.answer("❌ Не удалось получить список районов.")


@router.message(
    AuthStates.authenticated,
    RoleFilter(allowed=("supervisor","manager","admin")),
    Command("add_district"),
)
async def add_district_start(message: types.Message, state: FSMContext):
    await state.set_state(DistrictStates.waiting_for_district_data)
    await message.answer(
        "✏️ Введите новый район в формате:\n"
        "`Название_ru | Название_en | Название_hy | city_id`",
        parse_mode="Markdown",
    )


@router.message(AuthStates.authenticated, DistrictStates.waiting_for_district_data)
async def add_district_done(message: types.Message, state: FSMContext):
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 4 or not parts[3].isdigit():
        return await message.answer(
            "❌ Неверный формат. Пример:\n"
            "`Центр | Center | Կենտրոն | 42`",
            parse_mode="Markdown",
        )

    name_ru, name_en, name_hy, city_id = parts
    data = {
        "city_id": int(city_id),
        "name_ru":  name_ru,
        "name_en":  name_en,
        "name_hy":  name_hy,
        "name":     name_ru,
    }
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.post(f"{API_V1}/districts", json=data)

    if resp.status_code in (200, 201):
        district = resp.json().get("district") or resp.json().get("data")
        await message.answer(f"✅ Район создан: {district['id']} — {district['name_ru']}")
    else:
        await message.answer("❌ Не удалось создать район.")

    await state.reset_state(with_data=False)


@router.message(
    AuthStates.authenticated,
    RoleFilter(allowed=("supervisor","manager","admin")),
    Command("delete_district"),
)
async def delete_district_start(message: types.Message, state: FSMContext):
    await state.set_state(DistrictStates.waiting_for_delete_id)
    await message.answer("🗑 Введите ID района для удаления:")


@router.message(AuthStates.authenticated, DistrictStates.waiting_for_delete_id)
async def delete_district_done(message: types.Message, state: FSMContext):
    district_id = message.text.strip()
    if not district_id.isdigit():
        return await message.answer("❌ ID должен быть числом.")

    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as cli:
        resp = await cli.delete(f"{API_V1}/districts/{district_id}")

    if resp.status_code in (204, 200):
        await message.answer(f"✅ Район {district_id} удалён.")
    else:
        await message.answer("❌ Не удалось удалить район.")

    await state.reset_state(with_data=False)
