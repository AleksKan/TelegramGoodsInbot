# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.services.api_sqlite import get_paymentx


# Выбор способов пополнения
def refill_choice_finl():
    keyboard = InlineKeyboardMarkup()

    get_payments = get_paymentx()
    active_kb = []

    if get_payments['way_form'] == "True":
        active_kb.append(InlineKeyboardButton("📋 QIWI форма", callback_data="refill_choice:Form"))
    if get_payments['way_number'] == "True":
        active_kb.append(InlineKeyboardButton("📞 QIWI номер", callback_data="refill_choice:Number"))
    if get_payments['way_nickname'] == "True":
        active_kb.append(InlineKeyboardButton("Ⓜ QIWI никнейм", callback_data="refill_choice:Nickname"))
    if get_payments['way_formy'] == "True":
        active_kb.append(InlineKeyboardButton("📋 Yoo форма", callback_data="refill_choice:ForYm"))

    if len(active_kb) == 4:
        keyboard.add(active_kb[0], active_kb[1])
        keyboard.add(active_kb[2], active_kb[3])
    elif len(active_kb) == 3:
        keyboard.add(active_kb[0], active_kb[1])
        keyboard.add(active_kb[2])
    elif len(active_kb) == 2:
        keyboard.add(active_kb[0], active_kb[1])
    elif len(active_kb) == 1:
        keyboard.add(active_kb[0])
    else:
        keyboard = None

    if len(active_kb) >= 1:
        keyboard.add(InlineKeyboardButton("⬅ Вернуться ↩", callback_data="user_profile"))
        keyboard.add(InlineKeyboardButton("⬅ Вернуться в корзину ↩", callback_data="user_cart"))

    return keyboard


# Проверка киви платежа
def refill_bill_finl(send_requests, get_receipt, get_way):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🌀 Перейти к оплате", url=send_requests)
    ).add(
        InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"Pay:{get_way}:{get_receipt}")
    )

    return keyboard


# Кнопки при открытии самого товара
def products_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"add_item_cart:{position_id}")
    ).add(
        InlineKeyboardButton("💰 Купить товар", callback_data=f"buy_item_open:{position_id}:{remover}")
    ).add(
        InlineKeyboardButton("⬅ Вернуться ↩", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard


# Подтверждение сохранения адреса доставки
def accept_saved_adr(user_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Да, оставить текущий адрес", callback_data=f"user_cart"),
        InlineKeyboardButton("❌ Ввести новый адрес", callback_data=f"enter_address_manualy:{user_id}")
    )

    return keyboard

def accept_saved_phone(user_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Да, оставить текущий номер", callback_data=f"user_cart"),
        InlineKeyboardButton("❌ Ввести новый номер", callback_data=f"enter_phone_manualy:{user_id}")
    )

    return keyboard

# Подтверждение покупки товара
def products_addcart_confirm_finl(position_id, get_count):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"xaddcart_item:yes:{position_id}:{get_count}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"xaddcart_item:not:{position_id}:{get_count}")
    )

    return keyboard

# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"buy_item_confirm:yes:{position_id}:{get_count}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"buy_item_confirm:not:{position_id}:{get_count}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl(user_name):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💌 Написать в поддержку", url=f"https://t.me/{user_name}"),
    )

    return keyboard
