# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as ikb

from tgbot.services.api_sqlite import get_paymentx, get_settingsx, get_userx, update_settingsx, get_upaymentx, get_upaycount, create_upayments_row



# Поиск профиля
def sales_report_buttons(user_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("💰 Изменить баланс", callback_data=f"admin_user_balance_set:{user_id}"),
        ikb("💰 Выдать баланс", callback_data=f"admin_user_balance_add:{user_id}")
    ).add(
        ikb("🎁 Покупки", callback_data=f"admin_user_purchases:{user_id}"),
        ikb("💌 Отправить СМС", callback_data=f"admin_user_message:{user_id}")
    ).add(
        ikb("🔄 Обновить", callback_data=f"admin_user_refresh:{user_id}")
    )

    return keyboard



# Поиск профиля
def profile_search_finl(user_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("💰 Изменить баланс", callback_data=f"admin_user_balance_set:{user_id}"),
        ikb("💰 Выдать баланс", callback_data=f"admin_user_balance_add:{user_id}")
    ).add(
        ikb("🎁 Покупки", callback_data=f"admin_user_purchases:{user_id}"),
        ikb("💌 Отправить СМС", callback_data=f"admin_user_message:{user_id}")
    ).add(
        ikb("🔄 Обновить", callback_data=f"admin_user_refresh:{user_id}")
    )

    return keyboard

# Поиск профиля с запросом на продавца
def profile_search_reqs(user_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb(" Подтвердить запрос", callback_data=f"admin_user_request_approve:{user_id}"),
        ikb(" Отклонить запрос", callback_data=f"admin_user_request_decline:{user_id}"),
        ikb(" Удалить запрос", callback_data=f"admin_user_request_delete:{user_id}")
    )

    return keyboard


# Способы пополнения
def payment_choice_finl(user_id):
    keyboard = InlineKeyboardMarkup()
    #get_payments = get_paymentx()
    print("inline_admin")
    print(user_id)
    count = get_upaycount(user_id)
    print(count['paycount'])
    if count['paycount'] == 0:
        cur = create_upayments_row(user_id)
    else:
        get_payments = get_upaymentx(user_id)
    #get_payments = get_paymentx()
    print(get_payments)

    status_form_kb = ikb("✅", callback_data=f"change_payment:Form:False:{user_id}")
    status_number_kb = ikb("✅", callback_data=f"change_payment:Number:False:{user_id}")
    status_nickname_kb = ikb("✅", callback_data=f"change_payment:Nickname:False:{user_id}")
    status_formy_kb = ikb("✅", callback_data=f"change_payment:ForYm:False:{user_id}")

    if get_payments['way_form'] == "False":
        status_form_kb = ikb("❌", callback_data=f"change_payment:Form:True:{user_id}")
    if get_payments['way_number'] == "False":
        status_number_kb = ikb("❌", callback_data=f"change_payment:Number:True:{user_id}")
    if get_payments['way_nickname'] == "False":
        status_nickname_kb = ikb("❌", callback_data=f"change_payment:Nickname:True:{user_id}")
    if get_payments['way_formy'] == "False":
        status_formy_kb = ikb("❌", callback_data=f"change_payment:ForYm:True:{user_id}")

    keyboard.add(ikb("📋 По форме", url="https://vk.cc/bYjKGM"), status_form_kb)
    keyboard.add(ikb("📞 По номеру", url="https://vk.cc/bYjKEy"), status_number_kb)
    keyboard.add(ikb("Ⓜ По никнейму", url="https://vk.cc/c8s66X"), status_nickname_kb)
    keyboard.add(ikb("📋 По Yoo", url="https://vk.cc/bYjKGM"), status_formy_kb)

    return keyboard


# Кнопки с настройками
def settings_open_finl():
    keyboard = InlineKeyboardMarkup()
    get_settings = get_settingsx()

    if get_settings['misc_support'].isdigit():
        get_user = get_userx(user_id=get_settings['misc_support'])

        if get_user is not None:
            support_kb = ikb(f"@{get_user['user_login']} ✅", callback_data="settings_edit_support")
        else:
            support_kb = ikb("Не установлены ❌", callback_data="settings_edit_support")
            update_settingsx(misc_support="None")
    else:
        support_kb = ikb("Не установлены ❌", callback_data="settings_edit_support")

    if "None" == get_settings['misc_faq']:
        faq_kb = ikb("Не установлено ❌", callback_data="settings_edit_faq")
    else:
        faq_kb = ikb("Установлено ✅", callback_data="settings_edit_faq")

    if get_settings['type_trade'] is None:
        trade_type_kb = ikb("Тип не задан ❌", callback_data="settings_edit_trade_type")
    else:
        trade_type_kb = ikb(f"Тип плоащдки утановлен: {get_settings['type_trade']} ✅", callback_data="settings_edit_type_trade")

    keyboard.add(
        ikb("ℹ FAQ", callback_data="..."), faq_kb
    ).add(
        ikb("☎ Поддержка", callback_data="..."), support_kb
    ).add(
        ikb("☎ Тип площадки", callback_data="..."), trade_type_kb
    )


    return keyboard


# Выключатели
def turn_open_finl():
    keyboard = InlineKeyboardMarkup()
    get_settings = get_settingsx()

    if get_settings['status_buy'] == "True":
        status_buy_kb = ikb("Включены ✅", callback_data="turn_buy:False")
    elif get_settings['status_buy'] == "False":
        status_buy_kb = ikb("Выключены ❌", callback_data="turn_buy:True")

    if get_settings['status_work'] == "True":
        status_twork_kb = ikb("Включены ✅", callback_data="turn_twork:False")
    elif get_settings['status_work'] == "False":
        status_twork_kb = ikb("Выключены ❌", callback_data="turn_twork:True")

    if get_settings['status_refill'] == "True":
        status_pay_kb = ikb("Включены ✅", callback_data="turn_pay:False")
    else:
        status_pay_kb = ikb("Выключены ❌", callback_data="turn_pay:True")

    keyboard.row(ikb("⛔ Тех. работы", callback_data="..."), status_twork_kb)
    keyboard.row(ikb("💰 Пополнения", callback_data="..."), status_pay_kb)
    keyboard.row(ikb("🎁 Покупки", callback_data="..."), status_buy_kb)

    return keyboard

######################################## МАГАЗИНЫ ########################################
# Изменение магазина
def shop_name_edit_open_finl(shop_id, user_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🏷 Изм. название", callback_data=f"shop_edit_name:{shop_id}:{user_id}:{remover}"),
        ikb("❌ Удалить", callback_data=f"shop_edit_delete:{shop_id}:{user_id}:{remover}")
    ).add(
        ikb("⬅ Вернуться ↩", callback_data=f"shop_edit_return:{user_id}:{remover}")
    )

    return keyboard

# Изменение магазина
def shop_description_edit_open_finl(shop_id, user_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🏷 Изм. название", callback_data=f"shop_edit_description:{shop_id}:{user_id}:{remover}"),
        ikb("❌ Удалить", callback_data=f"shop_edit_delete:{shop_id}:{user_id}:{remover}")
    ).add(
        ikb("⬅ Вернуться ↩", callback_data=f"shop_edit_return:{user_id}:{remover}")
    )

    return keyboard
######################################## ТОВАРЫ ########################################
# Изменение категории
def category_edit_open_finl(category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🏷 Изм. название", callback_data=f"category_edit_name:{category_id}:{remover}"),
        ikb("❌ Удалить", callback_data=f"category_edit_delete:{category_id}:{remover}")
    ).add(
        ikb("⬅ Вернуться ↩", callback_data=f"category_edit_return:{remover}")
    )

    return keyboard

# Кнопки с удалением категории
def category_edit_delete_finl(category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Да, удалить", callback_data=f"category_delete:{category_id}:yes:{remover}"),
        ikb("✅ Нет, отменить", callback_data=f"category_delete:{category_id}:not:{remover}")
    )

    return keyboard

# Кнопки с удалением категории
def shop_edit_delete_finl(shop_id, remover):
    
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Да, удалить", callback_data=f"shop_delete:{shop_id}:yes:{remover}"),
        ikb("✅ Нет, отменить", callback_data=f"shop_delete:{shop_id}:not:{remover}")
    )

    return keyboard

# Кнопки при открытии позиции для изменения
def position_edit_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🏷 Изм. название", callback_data=f"position_edit_name:{position_id}:{category_id}:{remover}"),
        ikb("💰 Изм. цену", callback_data=f"position_edit_price:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("📜 Изм. описание", callback_data=f"position_edit_description:{position_id}:{category_id}:{remover}"),
        ikb("📸 Изм. фото", callback_data=f"position_edit_photo:{position_id}:{category_id}:{remover}"),
        # добавил 12.08.22    -----------------------------------------------------------
    ).add(
        ikb("📜 Изменить остаток", callback_data=f"position_edit_rest:{position_id}:{category_id}:{remover}"),
        ikb("📸 <---<ВП>-->", callback_data=f"position_edit_photo:{position_id}:{category_id}:{remover}"),
        # добавил 1.02.23    -----------------------------------------------------------
    ).add(
        ikb("🏙 Изм. город", callback_data=f"position_edit_city:{position_id}:{category_id}:{remover}"),
        ikb("🏙 Изм. магазин", callback_data=f"position_edit_shop:{position_id}:{category_id}:{remover}"),
        # -------------------------------------------------------------------------
    ).add(
        ikb("🗑 Очистить", callback_data=f"position_edit_clear:{position_id}:{category_id}:{remover}"),
        ikb("🎁 Добавить товары", callback_data=f"products_add_position:{position_id}:{category_id}"),
    ).add(
        ikb("📥 Товары", callback_data=f"position_edit_items:{position_id}:{category_id}:{remover}"),
        ikb("❌ Удалить", callback_data=f"position_edit_delete:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("⬅ Вернуться ↩", callback_data=f"position_edit_return:{category_id}:{remover}"),
    )

    return keyboard


# Кнопки при открытии позиции для изменения
def artist_edit_open_finl(artist_id, user_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🏷 Изм. название", callback_data=f"artist_edit_name:{artist_id}:{user_id}:{remover}"),
        ikb("🏙 Изм. город", callback_data=f"artist_edit_city:{artist_id}:{user_id}:{remover}"),
    ).add(
        ikb("📜 Изм. описание", callback_data=f"artist_edit_description:{artist_id}:{user_id}:{remover}"),
        ikb("📸 Изм. фото", callback_data=f"artist_edit_photo:{artist_id}:{user_id}:{remover}"),
    # -------------------------------------------------------------------------
    ).add(
        ikb("🗑 Очистить", callback_data=f"artist_edit_clear:{artist_id}:{user_id}:{remover}"),
        ikb("❌ Удалить", callback_data=f"artist_edit_delete:{artist_id}:{user_id}:{remover}"),
    ).add(
        ikb("⬅ Вернуться ↩", callback_data=f"artist_edit_return:{user_id}:{remover}"),
    )

    return keyboard

# Подтверждение удаления позиции
def artist_edit_delete_finl():
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Да, удалить", callback_data=f"artist_delete:yes:{position_id}:{category_id}:{remover}"),
        ikb("✅ Нет, отменить", callback_data=f"artist_delete:not:{position_id}:{category_id}:{remover}")
    )

    return keyboard




# Подтверждение удаления позиции
def position_edit_delete_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Да, удалить", callback_data=f"position_delete:yes:{position_id}:{category_id}:{remover}"),
        ikb("✅ Нет, отменить", callback_data=f"position_delete:not:{position_id}:{category_id}:{remover}")
    )

    return keyboard


# Подтверждение очистики позиции
def position_edit_clear_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Да, очистить", callback_data=f"position_clear:yes:{position_id}:{category_id}:{remover}"),
        ikb("✅ Нет, отменить", callback_data=f"position_clear:not:{position_id}:{category_id}:{remover}")
    )

    return keyboard

# Кнопки при открытии позиции для изменения
def shop_edit_open_finl(shop_id, remover, user_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🏷 Изм. название", callback_data=f"shop_edit_name:{shop_id}:{user_id}:{remover}"),
        ikb("💰 Изм. цену", callback_data=f"shop_edit_price:{shop_id}:{user_id}:{remover}"),
    ).add(
        ikb("📜 Изм. описание", callback_data=f"shop_edit_description:{shop_id}:{user_id}:{remover}"),
        ikb("📸 Изм. фото", callback_data=f"shop_edit_photo:{shop_id}:{user_id}:{remover}"),
        # добавил 12.08.22    -----------------------------------------------------------
    ).add(
        ikb("🏙 Изм. город", callback_data=f"shop_edit_city:{shop_id}:{user_id}:{remover}"),
        ikb("Для симметрии", callback_data=f"shop____edit_photo:{shop_id}:{user_id}:{remover}"),
        # -------------------------------------------------------------------------
    ).add(
        ikb("X🗑 Очистить", callback_data=f"shop_edit_clear:{shop_id}:{user_id}:{remover}"),
        ikb("X🎁 Добавить товары", callback_data=f"shop_add_position:{shop_id}:{user_id}"),
    ).add(
        #ikb("📥 Товары", callback_data=f"shop_edit_items:{shop_id}:{user_id}:{remover}"),
        ikb("❌ Удалить", callback_data=f"shop_edit_delete:{shop_id}:{user_id}:{remover}"),
    ).add(
        ikb("⬅ Вернуться ↩", callback_data=f"shop_edit_return:{user_id}:{remover}"),
    )

    return keyboard

# Подтверждение покупки товара
def shop_edit_delete_finl(shop_id, user_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("✅ Да, удалить", callback_data=f"shop_delete:yes:{shop_id}:{user_id}"),
        ikb("❌ Отменить удаление", callback_data=f"shop_delete:not:{shop_id}:{user_id}")
    )

    return keyboard