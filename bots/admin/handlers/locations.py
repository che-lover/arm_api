import os, httpx
from aiogram import Router, types
# from aiogram.filters.callback_query import CallbackQueryFilter
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin.handlers.auth import AuthStates

API_V1 = os.getenv('API_BASE_URL').rstrip('/') + '/v1'

class LocationsStates(StatesGroup):
    choose_action              = State()
    add_city                   = State()
    delete_city                = State()
    add_district_select_city   = State()
    add_district               = State()
    delete_district            = State()

router = Router()

async def show_locations_menu(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data.get("role")
    builder = InlineKeyboardBuilder()

    # Города
    builder.button(text="📜 Список городов", callback_data="loc_list_cities")
    if role in ("supervisor","admin","manager"):
        builder.button(text="➕ Добавить город",    callback_data="loc_add_city")
        builder.button(text="🗑 Удалить город",     callback_data="loc_delete_city")
    # Районы
    builder.button(text="📜 Список районов", callback_data="loc_list_districts")
    if role in ("supervisor","admin","manager"):
        builder.button(text="➕ Добавить район",   callback_data="loc_add_district")
        builder.button(text="🗑 Удалить район",    callback_data="loc_delete_district")
    # Назад
    builder.button(text="↩️ Назад", callback_data="back_to_main")
    builder.adjust(2)
    await msg.edit_text(
        "📍 *Управление локациями* — выберите действие:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )

# Вход из меню
@router.callback_query(
    AuthStates.authenticated,
    StateFilter("MainStates:choosing_scenario"),
    lambda c: c.data == "sc_locations"
)
async def enter_locations(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(LocationsStates.choose_action)
    await show_locations_menu(cq.message, state)

# Список городов
@router.callback_query(LocationsStates.choose_action, lambda c: c.data=="loc_list_cities")
async def loc_list_cities(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.get(f"{API_V1}/cities")
    if resp.status_code==200:
        cities = resp.json().get("data",[])
        text   = "\n".join(f"{c['id']} — {c.get('name_ru')}" for c in cities)
        await cq.message.answer("🏙 *Города:*\n"+text, parse_mode="Markdown")
    else:
        await cq.message.answer("❌ Ошибка получения городов.")
    await show_locations_menu(cq.message, state)

# Добавить город
@router.callback_query(LocationsStates.choose_action, lambda c: c.data=="loc_add_city")
async def start_add_city(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(LocationsStates.add_city)
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="loc_cancel")
    kb.adjust(1)
    await cq.message.edit_text(
        "✏️ Введите новый город:\n"
        "`Название_ru | Название_en | Название_hy`",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.message(LocationsStates.add_city)
async def process_add_city(msg: types.Message, state: FSMContext):
    parts = [p.strip() for p in msg.text.split("|")]
    if len(parts)<2:
        return await msg.answer("❌ Формат: `ru | en [| hy]`", parse_mode="Markdown")
    payload = {"name_ru":parts[0], "name_en":parts[1]}
    if len(parts)==3: payload["name_hy"]=parts[2]
    token   = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.post(f"{API_V1}/cities", json=payload)
    if resp.status_code in (200,201):
        city = resp.json().get("city") or resp.json().get("data")
        await msg.answer(f"✅ Город создан: {city['id']} — {city.get('name_ru')}")
    else:
        await msg.answer("❌ Не удалось создать город.")
    await state.set_state(LocationsStates.choose_action)
    await show_locations_menu(msg, state)

# Удалить город
@router.callback_query(LocationsStates.choose_action, lambda c: c.data=="loc_delete_city")
async def start_del_city(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(LocationsStates.delete_city)
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="loc_cancel")
    kb.adjust(1)
    await cq.message.edit_text("🗑 Введите ID города для удаления:", parse_mode="Markdown",
        reply_markup=kb.as_markup())

@router.message(LocationsStates.delete_city)
async def process_del_city(msg: types.Message, state: FSMContext):
    cid = msg.text.strip()
    if not cid.isdigit():
        return await msg.answer("❌ ID должен быть числом.")
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.delete(f"{API_V1}/cities/{cid}")
    if resp.status_code in (200,204):
        await msg.answer(f"✅ Город {cid} удалён.")
    else:
        await msg.answer("❌ Ошибка удаления.")
    await state.set_state(LocationsStates.choose_action)
    await show_locations_menu(msg, state)

# ===== для районов: сначала выбор города =====
@router.callback_query(LocationsStates.choose_action, lambda c: c.data=="loc_add_district")
async def start_add_district(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(LocationsStates.add_district_select_city)
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.get(f"{API_V1}/cities")
    if resp.status_code!=200:
        return await show_locations_menu(cq.message, state)
    cities = resp.json().get("data",[])
    b = InlineKeyboardBuilder()
    for c in cities:
        b.button(text=f"{c['id']}—{c['name_ru']}", callback_data=f"loc_city_{c['id']}")
    b.button(text="↩️ Отмена", callback_data="loc_back_to_loc_menu")
    b.adjust(1)
    await cq.message.edit_text("✏️ Выберите город:", reply_markup=b.as_markup())

@router.callback_query(LocationsStates.add_district_select_city, lambda c: c.data.startswith("loc_city_"))
async def choose_city_for_district(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    cid = int(cq.data.split("_")[-1])
    await state.update_data(city_id=cid)
    await state.set_state(LocationsStates.add_district)
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="loc_cancel")
    kb.adjust(1)
    await cq.message.edit_text(
        f"✏️ Введите район для города {cid}:\n"
        "`ru|en[|hy]`", parse_mode="Markdown", reply_markup=kb.as_markup()
    )

@router.callback_query(LocationsStates.add_district_select_city, lambda c: c.data=="loc_back_to_loc_menu")
async def cancel_add_district(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(LocationsStates.choose_action)
    await show_locations_menu(cq.message, state)

@router.message(LocationsStates.add_district)
async def process_add_district(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    cid  = data["city_id"]
    parts= [p.strip() for p in msg.text.split("|")]
    if len(parts)<2:
        return await msg.answer("❌ Формат: `ru|en[|hy]`", parse_mode="Markdown")
    payload = {"city_id":cid, "name_ru":parts[0], "name_en":parts[1]}
    if len(parts)==3: payload["name_hy"]=parts[2]
    token = data["token"]
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="loc_cancel")
    kb.adjust(1)
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.post(f"{API_V1}/districts", json=payload)
    if resp.status_code in (200,201):
        d = resp.json().get("district") or resp.json().get("data")
        await msg.answer(f"✅ Район создан: {d['id']} — {d['name_ru']}")
    else:
        await msg.answer("❌ Ошибка создания.", parse_mode="Markdown", reply_markup=kb.as_markup())
    await state.set_state(LocationsStates.choose_action)
    await show_locations_menu(msg, state)

# Список районов
@router.callback_query(LocationsStates.choose_action, lambda c: c.data=="loc_list_districts")
async def loc_list_districts(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.get(f"{API_V1}/districts")
    if resp.status_code==200:
        ds   = resp.json().get("data",[])
        text = "\n".join(f"{d['id']}—{d['name_ru']} (город {d['city_id']})" for d in ds)
        await cq.message.answer("🏘 Районы:\n"+text)
    else:
        await cq.message.answer("❌ Ошибка получения районов.")
    await show_locations_menu(cq.message, state)

# Удалить район
@router.callback_query(LocationsStates.choose_action, lambda c: c.data=="loc_delete_district")
async def start_del_district(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(LocationsStates.delete_district)
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="loc_cancel")
    kb.adjust(1)
    await cq.message.edit_text("🗑 Введите ID района для удаления:", parse_mode="Markdown", reply_markup=kb.as_markup())

@router.message(LocationsStates.delete_district)
async def process_del_district(msg: types.Message, state: FSMContext):
    rid = msg.text.strip()
    if not rid.isdigit():
        return await msg.answer("❌ ID должен быть числом.")
    token = (await state.get_data())["token"]
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"}) as cli:
        resp = await cli.delete(f"{API_V1}/districts/{rid}")
    if resp.status_code in (200,204):
        await msg.answer(f"✅ Район {rid} удалён.")
    else:
        await msg.answer("❌ Ошибка удаления.")
    await state.set_state(LocationsStates.choose_action)
    await show_locations_menu(msg, state)

# Назад в главное
@router.callback_query(LocationsStates.choose_action, lambda c: c.data=="back_to_main")
async def back_to_main(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    from admin.handlers.menu import cmd_menu
    await state.set_state("MainStates:choosing_scenario")
    await cmd_menu(cq.message, state)

@router.callback_query(lambda c: c.data=="loc_cancel", StateFilter(*LocationsStates))
async def loc_cancel(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Отменено", show_alert=True)
    await state.set_state(LocationsStates.choose_action)
    # показываем главное меню «Локаций»
    await show_locations_menu(cq.message, state)
