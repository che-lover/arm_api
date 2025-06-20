import logging
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShowcaseStates(StatesGroup):
    choose_action = State()
    add_select_city = State()
    add_select_district = State()
    add_select_item = State()
    add_select_packaging = State()
    add_confirm = State()
    add_upload_photo = State()

    view_select_city = State()
    view_select_district = State()
    view_manage_items = State()

    edit_enter_quantity = State()
    edit_upload_photo = State()
    edit_confirm = State()

    # Product CRUD
    prod_create_name = State()
    prod_create_desc = State()
    prod_confirm_create = State()
    prod_edit_select = State()
    prod_edit_field = State()
    prod_edit_value = State()
    prod_confirm_edit = State()

    # Packaging CRUD
    pack_create_select_prod = State()
    pack_create_volume = State()
    pack_create_price = State()
    pack_confirm_create = State()
    pack_edit_select = State()
    pack_edit_field = State()
    pack_edit_value = State()
    pack_confirm_edit = State()


async def show_showcase_menu(msg: types.Message, state: FSMContext):
    """Главное меню витрины: добавить товар / посмотреть витрину / назад"""
    data = await state.get_data()
    role = data["role"]

    builder = InlineKeyboardBuilder()
    # Курьеры и все админы/менеджеры
    builder.button(text="➕ Добавить товар", callback_data="sc_add_product")
    if role != 'courier':
        builder.button(text="📦 Создать товар", callback_data="sc_prod_create")
        builder.button(text="➕ Добавить фасовку", callback_data="sc_pack_create")
        builder.button(text="✏️ Редактировать фасовку", callback_data="sc_pack_edit")
        builder.button(text="✏️ Редактировать товар", callback_data="sc_prod_edit")
        builder.button(text="🛒 Просмотр витрины", callback_data="sc_view_showcase")

    builder.button(text="↩️ Назад", callback_data="back_to_main")
    builder.adjust(2)

    await msg.edit_text(
        "🛍 *Управление витриной* — выберите действие:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup(),
    )


# ———————————————
# 1) Входим в сценарий «витрина» из главного меню
# ———————————————
@router.callback_query(
    AuthStates.authenticated,
    StateFilter(MainStates.choosing_scenario),
    lambda c: c.data == "sc_showcase"
)
async def enter_showcase(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message, state)


# 2) Назад в главное меню бота из шага choose_action
@router.callback_query(ShowcaseStates.choose_action, lambda c: c.data == "back_to_main")
async def sc_back_to_main(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    from admin.handlers.menu import cmd_menu
    await state.set_state(MainStates.choosing_scenario)
    await cmd_menu(cq.message, state)


_INTERNAL = [
    ShowcaseStates.add_select_city,
    ShowcaseStates.add_select_district,
    ShowcaseStates.add_select_item,
    ShowcaseStates.add_select_packaging,
    ShowcaseStates.add_upload_photo,
    ShowcaseStates.view_select_city,
    ShowcaseStates.view_select_district,
    ShowcaseStates.view_manage_items,
]


@router.callback_query(StateFilter(*_INTERNAL), lambda c: c.data == "sc_back")
async def sc_back_to_showcase(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message, state)


@router.callback_query(ShowcaseStates.choose_action, lambda c: c.data == "sc_add_product")
async def sc_add_product(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(ShowcaseStates.add_select_city)

    # 2.1) получаем список городов
    token = (await state.get_data())["token"]
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).get(f"{API_V1}/cities")
    cities = resp.json().get("data", [])
    b = InlineKeyboardBuilder()
    for c in cities:
        b.button(text=f"{c['id']} — {c['name_ru']}", callback_data=f"sc_city_{c['id']}")
    b.button(text="↩️ Отмена", callback_data="sc_back")
    b.adjust(1)

    await cq.message.edit_text("✏️ Выберите город:", reply_markup=b.as_markup())


@router.callback_query(ShowcaseStates.add_select_city, lambda c: c.data.startswith("sc_city_"))
async def sc_choose_city(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    city_id = int(cq.data.split("_")[-1])
    await state.update_data(city_id=city_id)
    await state.set_state(ShowcaseStates.add_select_district)

    # GET /v1/districts и фильтрация по city_id
    token = (await state.get_data())["token"]
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).get(f"{API_V1}/districts")
    districts = [d for d in resp.json().get("data", []) if d["city_id"] == city_id]

    b = InlineKeyboardBuilder()
    for d in districts:
        b.button(text=f"{d['id']} — {d['name_ru']}", callback_data=f"sc_district_{d['id']}")
    b.button(text="↩️ Отмена", callback_data="sc_back")
    b.adjust(1)

    await cq.message.edit_text("✏️ Выберите район:", reply_markup=b.as_markup())


@router.callback_query(ShowcaseStates.add_select_district, lambda c: c.data.startswith("sc_district_"))
async def sc_choose_district(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    district_id = int(cq.data.split("_")[-1])
    await state.update_data(district_id=district_id)
    await state.set_state(ShowcaseStates.add_select_item)

    # GET /v1/products?city_id&district_id
    data = await state.get_data()
    token = data["token"]
    params = {"city_id": data["city_id"], "district_id": district_id}
    resp = await httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}).get(
        f"{API_V1}/products", params=params
    )
    products = resp.json().get("data", [])

    b = InlineKeyboardBuilder()
    for p in products:
        b.button(text=f"{p['id']} — {p.get('name_ru')}", callback_data=f"sc_prod_{p['id']}")
    b.button(text="↩️ Отмена", callback_data="sc_back")
    b.adjust(1)

    await cq.message.edit_text("✏️ Выберите товар:", reply_markup=b.as_markup())


@router.callback_query(ShowcaseStates.add_select_item, lambda c: c.data.startswith("sc_prod_"))
async def sc_choose_product(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    prod_id = int(cq.data.split("_")[-1])
    await state.update_data(product_id=prod_id)
    await state.set_state(ShowcaseStates.add_select_packaging)

    # GET /v1/products/{prod_id}
    token = (await state.get_data())["token"]
    resp = await httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}).get(
        f"{API_V1}/products/{prod_id}"
    )
    packagings = resp.json().get("data", {}).get("packagings", [])

    b = InlineKeyboardBuilder()
    for pack in packagings:
        text = f"{pack['id']} — {pack.get('name_ru') or pack.get('volume')}"
        b.button(text=text, callback_data=f"sc_pack_{pack['id']}")
    b.button(text="↩️ Отмена", callback_data="sc_back")
    b.adjust(1)

    await cq.message.edit_text("✏️ Выберите фасовку:", reply_markup=b.as_markup())


@router.callback_query(ShowcaseStates.add_select_packaging, lambda c: c.data.startswith("sc_pack_"))
async def sc_choose_packaging(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    pack_id = int(cq.data.split("_")[-1])
    await state.update_data(packaging_id=pack_id, quantity=1)
    await state.set_state(ShowcaseStates.add_upload_photo)
    await cq.message.edit_text(
        "📸 Теперь отправьте фото товара или /skip, чтобы пропустить:",
        parse_mode="Markdown"
    )

@router.message(ShowcaseStates.add_upload_photo)
async def sc_upload_photo(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]

    if msg.text == "/skip":
        photo_url = None
    elif msg.photo:
        file = await msg.bot.get_file(msg.photo[-1].file_id)
        photo_url = f"https://api.telegram.org/file/bot{msg.bot.token}/{file.file_path}"
    else:
        return await msg.answer("❌ Пришлите фото или /skip.")

    # сохраняем URL в state
    await state.update_data(photo_url=photo_url)

    # переходим в состояние подтверждения
    await state.set_state(ShowcaseStates.add_confirm)

    # строим клавиатуру
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить клад", callback_data="sc_confirm_add")
    builder.button(text="❌ Сбросить клад", callback_data="sc_cancel_add")
    builder.adjust(2)

    await msg.answer(
        "📋 Проверьте данные клада и выберите действие:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(ShowcaseStates.add_confirm, lambda c: c.data == "sc_confirm_add")
async def sc_confirm_add(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data = await state.get_data()
    token = data["token"]
    payload = {
        "city_id": data["city_id"],
        "district_id": data["district_id"],
        "packaging_id": data["packaging_id"],
        "quantity": data["quantity"],
        "photo_url": data["photo_url"],
        "status": "confirmed"
    }
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).post(f"{API_V1}/inventories", json=payload)

    if resp.status_code in (200, 201):
        inv = resp.json().get("inventory")
        await cq.message.answer(f"✅ Клад #{inv['id']} создан и подтверждён.")
    else:
        await cq.message.answer("❌ Ошибка при создании клада.")

    # обратно в меню витрины
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message, state)

@router.callback_query(ShowcaseStates.add_confirm, lambda c: c.data == "sc_cancel_add")
async def sc_cancel_add(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Операция отменена, выберите фасовку заново", show_alert=True)
    data = await state.get_data()
    prod_id = data["product_id"]

    # заново строим меню фасовок для этого товара
    token = data["token"]
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).get(f"{API_V1}/products/{prod_id}")
    packagings = resp.json().get("data", {}).get("packagings", [])

    builder = InlineKeyboardBuilder()
    for pack in packagings:
        text = pack.get("name") or pack.get("volume", "")
        builder.button(text=f"{pack['id']} — {text}", callback_data=f"sc_pack_{pack['id']}")
    builder.button(text="↩️ Назад", callback_data="sc_back")
    builder.adjust(1)

    await state.set_state(ShowcaseStates.add_select_packaging)
    await cq.message.edit_text("✏️ Выберите фасовку:", reply_markup=builder.as_markup())


@router.callback_query(ShowcaseStates.choose_action, lambda c: c.data == "sc_view_showcase")
async def sc_view_showcase(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(ShowcaseStates.view_select_city)

    token = (await state.get_data())["token"]
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).get(f"{API_V1}/cities")
    cities = resp.json().get("data", [])

    b = InlineKeyboardBuilder()
    for c in cities:
        b.button(text=f"{c['id']} — {c['name_ru']}", callback_data=f"vs_city_{c['id']}")
    b.button(text="↩️ Отмена", callback_data="sc_back")
    b.adjust(1)
    await cq.message.edit_text("🛒 Выберите город:", reply_markup=b.as_markup())


@router.callback_query(ShowcaseStates.view_select_city, lambda c: c.data.startswith("vs_city_"))
async def sc_vs_city(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    cid = int(cq.data.split("_")[-1])
    await state.update_data(city_id=cid)
    await state.set_state(ShowcaseStates.view_select_district)

    token = (await state.get_data())["token"]
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).get(f"{API_V1}/districts")
    districts = [d for d in resp.json().get("data", []) if d["city_id"] == cid]

    b = InlineKeyboardBuilder()
    for d in districts:
        b.button(text=f"{d['id']} — {d['name_ru']}", callback_data=f"vs_dist_{d['id']}")
    b.button(text="↩️ Отмена", callback_data="sc_back")
    b.adjust(1)
    await cq.message.edit_text("🛒 Выберите район:", reply_markup=b.as_markup())


@router.callback_query(ShowcaseStates.view_select_district, lambda c: c.data.startswith("vs_dist_"))
async def sc_vs_district(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    dist = int(cq.data.split("_")[-1])
    await state.update_data(district_id=dist)
    await state.set_state(ShowcaseStates.view_manage_items)

    # GET /v1/inventories?city_id&district_id&status=confirmed
    data = await state.get_data()
    token = data["token"]
    params = {"city_id": data["city_id"], "district_id": dist, "status": "confirmed"}
    resp = await httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}).get(
        f"{API_V1}/inventories", params=params
    )
    invs = resp.json().get("data", [])

    text = "\n".join(
        f"#{i['id']}: фасовка {i['packaging']['id']}, "
        f"кол-во {i['quantity']} г. Товар: {i['packaging']['product']['name_ru']}  "
        f'<a href="{i["photo_url"]}">ФОТО</a>'
        for i in invs
    )

    b = InlineKeyboardBuilder()
    for i in invs:
        b.button(text=f"❌ Удалить #{i['id']}", callback_data=f"inv_del_{i['id']}")
        b.button(text=f"✏️ Изменить #{i['id']}", callback_data=f"inv_edit_{i['id']}")
    b.button(text="↩️ Назад", callback_data="sc_view_showcase")
    b.adjust(1)

    await cq.message.edit_text("🛒 *Текущие клады:*\n" + text,
                               parse_mode="HTML",
                               reply_markup=b.as_markup(),
                               disable_web_page_preview=True)


@router.callback_query(ShowcaseStates.view_manage_items, lambda c: c.data.startswith("inv_edit_"))
async def sc_start_edit(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    inv_id = int(cq.data.split("_")[-1])
    await state.update_data(edit_inv_id=inv_id)

    # Получаем текущие данные клада
    token = (await state.get_data())["token"]
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).get(f"{API_V1}/inventories/{inv_id}")
    inv = resp.json().get("data", {})

    # Переходим в состояние ввода нового количества
    await state.set_state(ShowcaseStates.edit_enter_quantity)
    await cq.message.edit_text(
        f"✏️ Редактирование клада #{inv_id}\n"
        f"Текущее количество: {inv['quantity']}\n"
        f"Отправьте новое количество (целое число):"
    )


@router.message(ShowcaseStates.edit_enter_quantity)
async def sc_edit_enter_quantity(msg: types.Message, state: FSMContext):
    qty = msg.text.strip()
    if not qty.isdigit():
        return await msg.answer("❌ Количество должно быть целым числом.")
    await state.update_data(new_quantity=int(qty))
    await state.set_state(ShowcaseStates.edit_upload_photo)
    await msg.answer("📸 Пришлите новое фото или /skip, чтобы оставить старое:")


@router.message(ShowcaseStates.edit_upload_photo)
async def sc_edit_upload_photo(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if msg.text == "/skip":
        # признак оставить прежнее фото
        await state.update_data(new_photo_url=None, keep_old_photo=True)
    elif msg.photo:
        file = await msg.bot.get_file(msg.photo[-1].file_id)
        url = f"https://api.telegram.org/file/bot{msg.bot.token}/{file.file_path}"
        await state.update_data(new_photo_url=url, keep_old_photo=False)
    else:
        return await msg.answer("❌ Пришлите фотографию или /skip.")

    await state.set_state(ShowcaseStates.edit_confirm)

    b = InlineKeyboardBuilder()
    b.button(text="✅ Подтвердить изменения", callback_data="sc_confirm_edit")
    b.button(text="❌ Отменить", callback_data="sc_cancel_edit")
    b.adjust(2)

    await msg.answer(
        "📋 Проверьте новые данные и нажмите:",
        reply_markup=b.as_markup()
    )


@router.callback_query(ShowcaseStates.edit_confirm, lambda c: c.data == "sc_confirm_edit")
async def sc_confirm_edit(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data = await state.get_data()
    inv_id = data["edit_inv_id"]
    payload = {"quantity": data["new_quantity"]}
    # если пользователь загрузил новое фото
    if not data.get("keep_old_photo"):
        payload["photo_url"] = data.get("new_photo_url")

    token = data["token"]
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).put(f"{API_V1}/inventories/{inv_id}", json=payload)

    if resp.status_code == 200:
        await cq.message.answer(f"✅ Клад #{inv_id} обновлён.")
    else:
        await cq.message.answer("❌ Ошибка при обновлении.")

    # назад в главное меню витрины
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message, state)


@router.callback_query(ShowcaseStates.edit_confirm, lambda c: c.data == "sc_cancel_edit")
async def sc_cancel_edit(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Редактирование отменено", show_alert=True)
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message, state)


@router.callback_query(ShowcaseStates.view_manage_items, lambda c: c.data.startswith("inv_del_"))
async def sc_delete_inv(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    inv_id = int(cq.data.split("_")[-1])
    token = (await state.get_data())["token"]
    resp = await httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ).delete(f"{API_V1}/inventories/{inv_id}")
    if resp.status_code in (200, 204):
        await cq.message.answer(f"✅ Клад #{inv_id} удалён.")
    else:
        await cq.message.answer("❌ Ошибка при удалении.")
    # и обновляем список
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message, state)


@router.callback_query(ShowcaseStates.choose_action, lambda c: c.data == "sc_back")
async def sc_back(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    from admin.handlers.menu import cmd_menu
    await state.set_state(MainStates.choosing_scenario)
    await cmd_menu(cq.message, state)



# -------- Product Create --------
@router.callback_query(ShowcaseStates.choose_action, lambda c: c.data == "sc_prod_create")
async def sc_prod_create(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(ShowcaseStates.prod_create_name)
    await cq.message.edit_text("✏️ Введите название товара в формате RU|EN|HY:")

@router.message(ShowcaseStates.prod_create_name)
async def prod_name(msg: types.Message, state: FSMContext):
    parts = msg.text.split("|")
    if len(parts) != 3:
        return await msg.answer("❌ Формат: RU|EN|HY")
    await state.update_data(name_ru=parts[0].strip(), name_en=parts[1].strip(), name_hy=parts[2].strip())
    await state.set_state(ShowcaseStates.prod_create_desc)
    await msg.answer("✏️ Введите описание в формате RU|EN|HY:")

@router.message(ShowcaseStates.prod_create_desc)
async def prod_desc(msg: types.Message, state: FSMContext):
    parts = msg.text.split("|")
    if len(parts) != 3:
        return await msg.answer("❌ Формат: RU|EN|HY")
    await state.update_data(desc_ru=parts[0].strip(), desc_en=parts[1].strip(), desc_hy=parts[2].strip())
    data = await state.get_data()
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="sc_prod_confirm_create")
    kb.button(text="❌ Отменить", callback_data="sc_cancel_to_showcase")
    kb.adjust(2)
    text = (
        f"📋 Товар:\n"
        f"Name RU: {data['name_ru']}, EN: {data['name_en']}, HY: {data['name_hy']}\n"
        f"Desc RU: {data['desc_ru']}, EN: {data['desc_en']}, HY: {data['desc_hy']}"
    )
    await msg.answer(text, reply_markup=kb.as_markup())
    await state.set_state(ShowcaseStates.prod_confirm_create)

@router.callback_query(ShowcaseStates.prod_confirm_create, lambda c: c.data == "sc_prod_confirm_create")
async def prod_confirm_create(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data = await state.get_data()
    token = data['token']
    payload = {
        'name_ru': data['name_ru'], 'name_en': data['name_en'], 'name_hy': data['name_hy'],
        'description_ru': data['desc_ru'], 'description_en': data['desc_en'], 'description_hy': data['desc_hy']
    }
    logger.info("Sending create product request: %s", payload)
    resp = await httpx.AsyncClient(headers={'Authorization':f'Bearer {token}'}).post(f"{API_V1}/products", json=payload)
    if resp.status_code in (200,201):
        # logger.info("Product %s updated successfully", data['edit_prod_id'])
        prod = resp.json().get('data',{})
        await cq.message.answer(f"✅ Товар #{prod.get('id')} создан.")
    else:
        # logger.info("Product update failed: %s %s", resp.status_code, resp.text)
        await cq.message.answer("❌ Ошибка создания товара.")
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message, state)

# -------- Product Edit --------
@router.callback_query(ShowcaseStates.choose_action, lambda c: c.data == "sc_prod_edit")
async def sc_prod_edit(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token = (await state.get_data())['token']
    resp = await httpx.AsyncClient(headers={'Authorization':f'Bearer {token}'}).get(f"{API_V1}/products")
    prods = resp.json().get('data',[])
    kb = InlineKeyboardBuilder()
    for p in prods:
        kb.button(text=f"{p['id']} — {p['name_ru']}", callback_data=f"prod_edit_{p['id']}")
    kb.button(text="↩️ Отмена", callback_data="sc_cancel_to_showcase")
    kb.adjust(1)
    await cq.message.edit_text("✏️ Выберите товар для редактирования:", reply_markup=kb.as_markup())

@router.callback_query(ShowcaseStates.prod_edit_select, lambda c: c.data.startswith("prod_edit_"))
async def prod_edit_select(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    pid = int(cq.data.split("_")[-1])
    await state.update_data(edit_prod_id=pid)
    # choose field
    kb = InlineKeyboardBuilder()
    for fld in ['name_ru','name_en','name_hy','description_ru','description_en','description_hy']:
        kb.button(text=fld, callback_data=f"prod_field_{fld}")
    kb.button(text="↩️ Отмена", callback_data="sc_cancel_to_showcase")
    kb.adjust(2)
    await state.set_state(ShowcaseStates.prod_edit_field)
    await cq.message.edit_text("Выберите поле для редактирования:", reply_markup=kb.as_markup())

@router.callback_query(ShowcaseStates.prod_edit_field, lambda c: c.data.startswith("prod_field_"))
async def prod_edit_field(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    field = cq.data.split("_")[-1]
    await state.update_data(edit_field=field)
    await state.set_state(ShowcaseStates.prod_edit_value)
    await cq.message.edit_text(f"Введите новое значение для {field}:")

@router.message(ShowcaseStates.prod_edit_value)
async def prod_edit_value(msg: types.Message, state: FSMContext):
    await state.update_data(edit_value=msg.text)
    data = await state.get_data()
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="sc_prod_confirm_edit")
    kb.button(text="❌ Отмена", callback_data="sc_cancel_to_showcase")
    kb.adjust(2)
    await msg.answer(f"Подтвердить изменение {data['edit_field']} -> {data['edit_value']}?", reply_markup=kb.as_markup())
    await state.set_state(ShowcaseStates.prod_confirm_edit)

@router.callback_query(ShowcaseStates.prod_confirm_edit, lambda c: c.data=="sc_prod_confirm_edit")
async def prod_confirm_edit(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data=await state.get_data(); token=data['token']
    payload={data['edit_field']: data['edit_value']}
    resp=await httpx.AsyncClient(headers={'Authorization':f'Bearer {token}'}).put(
        f"{API_V1}/products/{data['edit_prod_id']}", json=payload
    )
    if resp.status_code==200:
        await cq.message.answer(f"✅ Товар #{data['edit_prod_id']} обновлён.")
    else:
        await cq.message.answer("❌ Ошибка обновления.")
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message,state)

# -------- Packaging Create --------
@router.callback_query(ShowcaseStates.choose_action, lambda c: c.data == "sc_pack_create")
async def sc_pack_create(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token=(await state.get_data())['token']
    resp=await httpx.AsyncClient(headers={'Authorization':f'Bearer {token}'}).get(f"{API_V1}/products")
    prods=resp.json().get('data',[])
    kb=InlineKeyboardBuilder()
    for p in prods:
        kb.button(text=f"{p['id']} — {p['name_ru']}", callback_data=f"pack_create_prod_{p['id']}")
    kb.button(text="↩️ Отмена", callback_data="sc_cancel_to_showcase")
    kb.adjust(1)
    await state.set_state(ShowcaseStates.pack_create_select_prod)
    await cq.message.edit_text("✏️ Выберите товар для фасовки:", reply_markup=kb.as_markup())

@router.callback_query(ShowcaseStates.pack_create_select_prod, lambda c: c.data.startswith("pack_create_prod_"))
async def pack_select_prod(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    pid=int(cq.data.split("_")[-1]); await state.update_data(pack_prod_id=pid)
    await state.set_state(ShowcaseStates.pack_create_volume)
    await cq.message.edit_text("✏️ Введите объём фасовки (число):")

@router.message(ShowcaseStates.pack_create_volume)
async def pack_volume(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit(): return await msg.answer("❌ Целое число")
    await state.update_data(pack_volume=int(msg.text))
    await state.set_state(ShowcaseStates.pack_create_price)
    await msg.answer("✏️ Введите цену фасовки:")

@router.message(ShowcaseStates.pack_create_price)
async def pack_price(msg: types.Message, state: FSMContext):
    try: price=float(msg.text)
    except: return await msg.answer("❌ Число")
    await state.update_data(pack_price=price)
    data=await state.get_data()
    kb=InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="sc_pack_confirm_create")
    kb.button(text="❌ Отменить", callback_data="sc_cancel_to_showcase")
    kb.adjust(2)
    text=f"📋 Фасовка: prod={data['pack_prod_id']}, vol={data['pack_volume']}, price={data['pack_price']}"
    await msg.answer(text, reply_markup=kb.as_markup())
    await state.set_state(ShowcaseStates.pack_confirm_create)

@router.callback_query(ShowcaseStates.pack_confirm_create, lambda c: c.data=="sc_pack_confirm_create")
async def pack_confirm_create(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data=await state.get_data(); token=data['token']
    payload={'product_id':data['pack_prod_id'],'volume':data['pack_volume'],'price':data['pack_price']}
    resp=await httpx.AsyncClient(headers={'Authorization':f'Bearer {token}'}).post(f"{API_V1}/packagings",json=payload)
    if resp.status_code in (200,201): pack=resp.json().get('data',{}); await cq.message.answer(f"✅ Фасовка #{pack.get('id')} создана.")
    else: await cq.message.answer("❌ Ошибка создания фасовки.")
    await state.set_state(ShowcaseStates.choose_action); await show_showcase_menu(cq.message,state)

# -------- Packaging Edit --------
@router.callback_query(ShowcaseStates.choose_action, lambda c: c.data == "sc_pack_edit")
async def sc_pack_edit(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    token=(await state.get_data())['token']
    resp=await httpx.AsyncClient(headers={'Authorization':f'Bearer {token}'}).get(f"{API_V1}/packagings")
    packs=resp.json().get('data',[])
    kb=InlineKeyboardBuilder()
    for p in packs:
        kb.button(text=f"{p['id']} — vol:{p['volume']}", callback_data=f"pack_edit_{p['id']}")
    kb.button(text="↩️ Отмена", callback_data="sc_cancel_to_showcase")
    kb.adjust(1)
    await state.set_state(ShowcaseStates.pack_edit_select)
    await cq.message.edit_text("✏️ Выберите фасовку для редактирования:", reply_markup=kb.as_markup())

@router.callback_query(ShowcaseStates.pack_edit_select, lambda c: c.data.startswith("pack_edit_"))
async def pack_edit_select(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer(); pid=int(cq.data.split("_")[-1]); await state.update_data(edit_pack_id=pid)
    kb=InlineKeyboardBuilder()
    for fld in ['product_id','volume','price']:
        kb.button(text=fld, callback_data=f"pack_field_{fld}")
    kb.button(text="↩️ Отмена", callback_data="sc_cancel_to_showcase")
    kb.adjust(2)
    await state.set_state(ShowcaseStates.pack_edit_field)
    await cq.message.edit_text("Выберите поле:",reply_markup=kb.as_markup())

@router.callback_query(ShowcaseStates.pack_edit_field, lambda c: c.data.startswith("pack_field_"))
async def pack_edit_field(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer(); fld=cq.data.split("_")[-1]; await state.update_data(edit_pack_field=fld)
    await state.set_state(ShowcaseStates.pack_edit_value)
    await cq.message.edit_text(f"Введите новое значение для {fld}:")

@router.message(ShowcaseStates.pack_edit_value)
async def pack_edit_value(msg: types.Message, state: FSMContext):
    await state.update_data(edit_pack_val=msg.text)
    kb=InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="sc_pack_confirm_edit")
    kb.button(text="❌ Отменить", callback_data="sc_cancel_to_showcase")
    kb.adjust(2)
    await msg.answer(f"Подтвердить {msg.text}?",reply_markup=kb.as_markup())
    await state.set_state(ShowcaseStates.pack_confirm_edit)

@router.callback_query(ShowcaseStates.pack_confirm_edit, lambda c: c.data=="sc_pack_confirm_edit")
async def pack_confirm_edit(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer(); data=await state.get_data(); token=data['token']
    payload={data['edit_pack_field']: data['edit_pack_val']}
    resp=await httpx.AsyncClient(headers={'Authorization':f'Bearer {token}'}).put(
        f"{API_V1}/packagings/{data['edit_pack_id']}", json=payload)
    if resp.status_code==200: await cq.message.answer(f"✅ Фасовка #{data['edit_pack_id']} обновлена.")
    else: await cq.message.answer("❌ Ошибка.")
    await state.set_state(ShowcaseStates.choose_action); await show_showcase_menu(cq.message,state)

@router.callback_query(lambda c: c.data == "sc_cancel_to_showcase", StateFilter(*ShowcaseStates))
async def sc_cancel_to_showcase(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer("❌ Отменено", show_alert=True)
    await state.set_state(ShowcaseStates.choose_action)
    await show_showcase_menu(cq.message, state)
