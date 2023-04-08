# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

import gettext
from pathlib import Path
from contextvars import ContextVar

from tgbot.keyboards.inline_user import refill_bill_finl, refill_choice_finl
from tgbot.loader import dp
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_yoo import YooAPI
from tgbot.services.api_cb import CoinbaseAPI
#from yoomoney import Client as ClientYoo
from tgbot.services.api_sqlite import update_userx, get_refillx, add_refillx, get_userx, get_user_lang
from tgbot.utils.const_functions import get_date, get_unix
from tgbot.utils.misc_functions import send_admins
from babel import Locale
from tgbot.data.config import get_admins, BOT_DESCRIPTION, I18N_DOMAIN, LOCALES_DIR
#from tgbot.middlewares.i18n import I18nMiddleware
#from aiogram.contrib.middlewares.i18n import I18nMiddleware
from tgbot.middlewares.i18n import I18nMiddleware

i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)

print(i18n)
_ = i18n.gettext

min_input_qiwi = 5  # Минимальная сумма пополнения в рублях
min_input_yoo = 5

# Выбор способа пополнения
@dp.callback_query_handler(text="user_refill", state="*")
async def refill_way(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    print(user_id)
    lang = get_user_lang(user_id)['user_lang']
    print(lang)
    get_kb = refill_choice_finl(lang)

    if get_kb is not None:
        await call.message.edit_text(_("<b>💰 Выберите способ пополнения</b>", locale=lang), reply_markup=get_kb)
    else:
        await call.answer(_("⛔ Пополнение временно недоступно", locale=lang), True)

# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="refill_choice", state="*")
async def refill_way_choice(call: CallbackQuery, state: FSMContext):
    get_way = call.data.split(":")[1]
    user_id = call.from_user.id
    print(user_id)
    lang = get_user_lang(user_id)['user_lang']
    print(lang)

    await state.update_data(here_pay_way=get_way)

    await state.set_state("here_pay_amount")
    await call.message.edit_text(_("<b>💰 Введите сумму пополнения</b>", locale=lang))


###################################################################################
#################################### ВВОД СУММЫ ###################################
# Принятие суммы для пополнения средств через QIWI и YooMoney
@dp.message_handler(state="here_pay_amount")
async def refill_get(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_userx(user_id=user_id)['user_lang']
    if message.text.isdigit():
        cache_message = await message.answer(_("<b>♻ Подождите, платёж генерируется...</b>", locale=lang))
        pay_amount = int(message.text)
        pay_user_id = int(message.from_user.id)
        print(cache_message)

        if min_input_qiwi <= pay_amount <= 300000:
            get_way = (await state.get_data())['here_pay_way']
            
            await state.finish()
            if get_way == 'Form':
                get_message, get_link, receipt = await (
                    await QiwiAPI(cache_message, user_bill_pass=True)
                ).bill_pay(pay_amount, get_way)
            elif get_way == 'ForYm':
                print("test")
                print(pay_amount, get_way)

                get_message, get_link, receipt = await (
                    await YooAPI(cache_message)
                ).bill_pay(pay_amount, get_way, lang)
                print(get_message, get_link, receipt)
            elif get_way == 'CoinBase':
                print("test")
                print(pay_amount, get_way)
                get_link = "https://ya.ru"

                get_message, receipt = await (
                    await CoinbaseAPI(cache_message)
                ).bill_pay(pay_amount, get_way)
                print(get_message, receipt)

            if get_message:
                await cache_message.edit_text(get_message, reply_markup=refill_bill_finl(get_link, receipt, get_way, lang))
        else:
            await cache_message.edit_text(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer(_("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств", locale=lang))



###################################################################################
################################ ПРОВЕРКА ПЛАТЕЖЕЙ ################################
# Проверка оплаты через форму QIWI
@dp.callback_query_handler(text_contains="Pay:Form")
async def refill_check_form(call: CallbackQuery):
    receipt = call.data.split(":")[2]
    user_id = call.message.from_user.id
    pay_scheme = 2

    if pay_scheme == 1:
        pay_status, pay_amount = await (
            await QiwiAPI(call, user_check_pass=True)
        ).check_form(receipt)

    elif pay_scheme == 2:
        pay_status, pay_amount = await (
            await QiwiAPI(call, suser_id=user_id, user_check_pass=True)
        ).check_form(receipt)

    if pay_status == "PAID":
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, "Form")
        else:
            await call.answer(_("❗ Ваше пополнение уже было зачислено.", locale=lang), True)
    elif pay_status == "EXPIRED":
        await call.message.edit_text(_("<b>❌ Время оплаты вышло. Платёж был удалён.</b>", locale=lang))
    elif pay_status == "WAITING":
        await call.answer(_("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", locale=lang), True, cache_time=5)
    elif pay_status == "REJECTED":
        await call.message.edit_text(_("<b>❌ Счёт был отклонён.</b>", locale=lang))


# Проверка оплаты через форму Yoo
@dp.callback_query_handler(text_contains="Pay:ForYm")
async def refill_check_formy(call: CallbackQuery):
    print("UT 115")
    receipt = call.data.split(":")[2]
    print(call.data)
    print(receipt)
    suid=call.from_user.id

    pay_status, pay_amount = await (
        await YooAPI(suid=suid)
    ).check_formy(receipt)

    print(pay_status, pay_amount)

    if pay_status == "success":
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, "ForYm")
        else:
            await call.answer(_("❗ Ваше пополнение уже было зачислено.", locale=lang), True)
    elif pay_status == "EXPIRED":
        await call.message.edit_text(_("<b>❌ Время оплаты вышло. Платёж был удалён.</b>", locale=lang))
    elif pay_status == "WAITING":
        await call.answer(_("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", locale=lang), True, cache_time=5)
    elif pay_status == "REJECTED":
        await call.message.edit_text(_("<b>❌ Счёт был отклонён.</b>", locale=lang))


# Проверка оплаты по переводу (по нику или номеру)
@dp.callback_query_handler(text_startswith=['Pay:Number', 'Pay:Nickname'])
async def refill_check_send(call: CallbackQuery):
    way_pay = call.data.split(":")[1]
    receipt = call.data.split(":")[2]
    user_id = call.message.from_user.id

    pay_status, pay_amount = await (
        await QiwiAPI(call, suser_id=user_id, user_check_pass=True)
    ).check_send(receipt)

    if pay_status == 1:
        await call.answer(_("❗ Оплата была произведена не в рублях.", locale=lang), True, cache_time=5)
    elif pay_status == 2:
        await call.answer(_("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", locale=lang), True, cache_time=5)
    elif pay_status != 4:
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, way_pay)
        else:
            await call.answer(_("❗ Ваше пополнение уже зачислено.", locale=lang), True, cache_time=60)


##########################################################################################
######################################### ПРОЧЕЕ #########################################
# Зачисление средств
async def refill_success(call: CallbackQuery, receipt, amount, get_way):
    get_user = get_userx(user_id=call.from_user.id)

    add_refillx(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt,
                amount, receipt, get_way, get_date(), get_unix())

    update_userx(call.from_user.id,
                 user_balance=get_user['user_balance'] + amount,
                 user_refill=get_user['user_refill'] + amount)

    await call.message.edit_text(f"<b>💰 Вы пополнили баланс на сумму <code>{amount}₽</code>. Удачи ❤\n"
                                 f"🧾 Чек: <code>#{receipt}</code></b>")

    await send_admins(
        f"👤 Пользователь: <b>@{get_user['user_login']}</b> | <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> | <code>{get_user['user_id']}</code>\n"
        f"💰 Сумма пополнения: <code>{amount}₽</code>\n"
        f"🧾 Чек: <code>#{receipt}</code>"
    )
