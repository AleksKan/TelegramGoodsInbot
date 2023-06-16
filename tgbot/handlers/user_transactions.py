# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
import asyncio
#from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import datetime
import requests
import json
import gettext
import decimal
from pathlib import Path
from contextvars import ContextVar

from tgbot.keyboards.inline_user import refill_bill_finl, refill_choice_finl, refill_bill_crypto_finl
from tgbot.loader import dp
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_yoo import YooAPI
#from tgbot.services.api_cb import CoinbaseAPI
#from tgbot.services.api_crypto import BinanceAPI
from tgbot.services.api_tron import TronAPI
#import tronpy
#from yoomoney import Client as ClientYoo
from tgbot.services.api_sqlite import update_userx, get_refillx, add_refillx, get_userx, get_user_lang, add_prepay, create_crypto_payment_row, get_tron_address, get_crypto_address, get_system_crypto_address, get_system_tron_address
from tgbot.utils.const_functions import get_date, get_unix
from tgbot.utils.misc_functions import send_admins, catch_transactions20m, address_to_hex, check_trx_now, check_btc_now
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

def get_tron_prices():
    url = 'https://apilist.tronscanapi.com/api/search/hot'
    payload = {}
    response = requests.get(url, payload)
    data = json.loads(response.text)

    return data

def GetTronPrice():
    try:
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=TRXUSDT'
        payload = {}
        #req = requests.get("https://api-pub.bitfinex.com/v2/ticker/tTRXUSD")
        cresponse = requests.get(url, payload)
        print(cresponse)
        response = json.loads(cresponse.text)
        trxusdt_price = response['price']
        return trxusdt_price
    except Exception:
        raise Exception("Damn...Something was wrong...")

def GetUSDTPrice():
    try:
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB'
        payload = {}
        #req = requests.get("https://api-pub.bitfinex.com/v2/ticker/tTRXUSD")
        cresponse = requests.get(url, payload)
        print(cresponse)
        response = json.loads(cresponse.text)
        priceusdt = response['price']
        return priceusdt
    except Exception:
        raise Exception("Damn...Something was wrong...")


def GetBtcPrice():
    try:
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCRUB'
        payload = {}
        #req = requests.get("https://api-pub.bitfinex.com/v2/ticker/tTRXUSD")
        cresponse = requests.get(url, payload)
        print(cresponse)
        response = json.loads(cresponse.text)
        btc_price = response['price']
        return btc_price
    except Exception:
        raise Exception("Damn...Something was wrong...")

def getTokens():
    url = "https://apilist.tronscan.org/api/token"
    response = requests.get(url)
    tokens = response.json()

    return tokens

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

# Изменение адреса в сети Tron TRC20
@dp.callback_query_handler(text_startswith="change_trc20", state="*")
async def change_trc20(call: CallbackQuery, state: FSMContext):
    tron_address = get_tron_address(call.from_user.id)
    trx_addr_txt = ""
    if tron_address: trx_addr_txt = f"<b>Ваш текущий Tron TRC20 адрес</b>: {tron_address['tron_address']}\n"
    await state.set_state("here_tron_address")
    await call.message.edit_text(f"{trx_addr_txt}\n "
                                 f"Введите адрес TRC20 с которого планируете пополнять баланс")

# Изменение адреса в сети Tron TRC20
@dp.callback_query_handler(text_startswith="change_bep20", state="*")
async def change_trc20(call: CallbackQuery, state: FSMContext):
    btcb_address = get_crypto_address(call.from_user.id, "BTCB")
    btcb_addr_txt = ""
    if btcb_address: btcb_addr_txt = f"<b>Ваш текущий BTC BEP20 адрес</b>: {btcb_address['tron_address']}\n"
    await state.set_state("here_crypto_address")
    await call.message.edit_text(f"{btcb_addr_txt}\n "
                                 f"Введите адрес BTC BEP20 с которого планируете пополнять баланс")


# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="refill_choice", state="*")
async def refill_way_choice(call: CallbackQuery, state: FSMContext):
    get_way = call.data.split(":")[1]
    #user_id = call.from_user.id
    print("OKKKK1")
    print(get_way)

    if get_way == "Tron":
        type_net = call.data.split(":")[2]
        print(type_net)
        await state.update_data(here_type_net=type_net)

    await state.update_data(here_pay_way=get_way)

    if get_way == 'Tron':
        tron_address = get_tron_address(call.from_user.id)
        if tron_address:
            print(tron_address)
            await state.update_data(here_tron_address=tron_address['tron_address'])
            await state.set_state("here_pay_amount")
            await call.message.edit_text("<b>💰 Введите сумму пополнения в рублях</b>")

        else:
            print("TRON ADDRESS NOT EXIST")
            await state.set_state("here_tron_address")
            await call.message.edit_text("Введите адрес с которого планируете пополнить баланс")

    if get_way == 'BTCB':
        crypto_address = get_crypto_address(call.from_user.id, get_way)
        await state.update_data(here_type_net=get_way)
        if crypto_address:
            print(crypto_address)
            await state.update_data(here_crypto_address=crypto_address['tron_address'])
            await state.set_state("here_pay_amount")
            await call.message.edit_text("<b>💰 Введите сумму пополнения в рублях</b>")

        else:
            print("BTCB ADDRESS NOT EXIST")
            await state.set_state("here_crypto_address")
            await call.message.edit_text("Введите адрес с которого планируете пополнить баланс")


###################################################################################
#################################### ВВОД СУММЫ ###################################
# Принятие суммы для пополнения средств через QIWI
@dp.message_handler(state="here_pay_amount")
async def refill_get(message: Message, state: FSMContext):
    if message.text.isdigit():
        cache_message = await message.answer("<b>♻ Подождите, платёж генерируется...</b>")
        pay_amount = int(message.text)

        if min_input_qiwi <= pay_amount <= 300000:
            get_way = (await state.get_data())['here_pay_way']
            #await state.finish()

            if get_way == "Form" or get_way == "Nickname" or get_way == "Number":
                get_message, get_link, receipt = await (
                    await QiwiAPI(cache_message, user_bill_pass=True)
                ).bill_pay(pay_amount, get_way)

            if get_way == "Tron" or get_way == "BTCB":
                receipt = str(int(time.time() * 100))
                await state.update_data(here_receipt=receipt)
                if get_way == "Tron":
                    type_net = (await state.get_data())['here_type_net']
                    address_from = (await state.get_data())['here_tron_address']
                if get_way == "BTCB":
                    type_net = (await state.get_data())['here_type_net']
                    address_from = (await state.get_data())['here_crypto_address']

                if type_net == "USDT":
                    coinprice = GetUSDTPrice()
                    #coinprice = 78.18000000
                    net_name = "TRC20"
                    priceincoin = round(pay_amount / float(coinprice), 9)
                    print(priceincoin)
                    priceincoinq = round(priceincoin, 9)
                    print(priceincoinq)

                elif type_net == "BTCB":
                    coinprice = GetBtcPrice()
                    net_name = "BEP20"
                    coinpriceUSDT = GetUSDTPrice()
                    priceincoin = round(pay_amount / float(coinpriceUSDT) / float(coinprice), 9)
                    print(priceincoin)
                    priceincoinq = round(priceincoin, 9)
                    print(priceincoinq)

                elif type_net == "TRX":
                    coinprice = GetTronPrice()
                    coinpriceUSDT = GetUSDTPrice()
                    net_name = "TRC20"
                    priceincoin = round(pay_amount / float(coinpriceUSDT) / float(coinprice), 9)
                    print(priceincoin)
                    priceincoinq = round(priceincoin, 9)
                    print(priceincoinq)

                print(pay_amount, type_net, coinprice)


                #address_to = "TQanL97TYygHiycDZ1up8XNqt1mHcGJ4Nv"
                #adddress_to = (await state.get_data())['here_crypto_address'] #(await state.get_data())['here_tron_address']
                address_to = get_system_crypto_address(type_net)
                get_message = f"<b>🆙 Пополнение баланса крипто валютой {type_net}</b>\n" \
                              f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                              f" Для пополнения баланса, нажмите на кнопку ниже \n" \
                              f"<code>Перейти к оплате</code> и оплатите выставленный вам счёт\n" \
                              f"❗ У вас имеется 30 минут на оплату счета.\n" \
                              f"❗ Адрес в сети {net_name}: {address_to['tron_address']}\n" \
                              f"❗ Текущая цена {type_net}: {coinprice} \n" \
                              f"💰 Сумма пополнения в {type_net}: <code>{priceincoin:.6f} </code>\n" \
                              f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                              f"❗ Ожидается транзакция с адреса: {address_from}\n" \
                              f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"

            if get_way == "Form" or get_way == "Nickname" or get_way == "Number":
                get_message = f"<b>🆙 Пополнение баланса</b>\n" \
                              f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                              f" Для пополнения баланса, нажмите на кнопку ниже \n" \
                              f"<code>Перейти к оплате</code> и оплатите выставленный вам счёт\n" \
                              f"❗ У вас имеется 30 минут на оплату счета.\n" \
                              f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                              f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"


                #wallet = 'TQanL97TYygHiycDZ1up8XNqt1mHcGJ4Nv'
                #address_to = (await state.get_data())['here_tron_address']
                #trxs = await get_trx(address_to)
                #print(trxs)

            await state.set_state("here_pay_check")
            lang = "ru"

            if get_way in ["Tron", "BTCB"] and get_message:
                #tron_address = (await state.get_data())['here_tron_address']
                await cache_message.edit_text(get_message, reply_markup=refill_bill_crypto_finl(get_way, type_net, receipt, lang))

            if get_way != "Tron" and get_way != "BTCB":
                await cache_message.edit_text(get_message, reply_markup=refill_bill_finl(get_link, receipt, get_way))
        else:
            await cache_message.edit_text(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")

async def get_trx(address_to):
    url = f"https://api.trongrid.io/v1/accounts/{address_to}/transactions?only_confirmed=true&only_to=true"

    response = await requests.get(url, headers={"TRON-PRO-API-KEY": "5c4c149e-83d1-4926-8d73-78dac1ab2d38"})

    if response.status_code == 200:
        total = 0
        transactions = json.loads(response.text)["data"]
        for tx in transactions:
            if tx["raw_data"]["contract"][0]["parameter"]["value"]["to_address"] == address_to and tx["raw_data"]["contract"][0]["parameter"]["value"]["amount"] > 0:
                #if tx["raw_data"]["contract"][0]["parameter"]["value"]["owner_address"] == address_from:
                total += tx["raw_data"]["contract"][0]["parameter"]["value"]["amount"]
                #print(tx["raw_data"]["contract"], total)
                return tx["raw_data"]["contract"]

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


# Проверка оплаты через сеть TronNet
@dp.callback_query_handler(text_contains="Pay:Tron", state="*")  #text_contains text_startswith
async def refill_check_tron(call: CallbackQuery, state: FSMContext):
    print("UT 336")
    get_way = call.data.split(":")[1]
    type_net = call.data.split(":")[2]
    receipt = call.data.split(":")[3]
    user_id = call.from_user.id
    print(type_net, receipt)

    await state.update_data(here_type_net=type_net)
    await call.answer(f"♻ Подождите, платёж проверяется...")


    #address_to = 'TQanL97TYygHiycDZ1up8XNqt1mHcGJ4Nv'
    address_to = get_system_crypto_address(type_net)['tron_address']


    address_from = (await state.get_data())['here_tron_address']

    print(address_to, address_from)
    st = get_unix()
    #print(wallet, tron_address)
    #catch_transactions20m(tron_address, wallet)
    #await catch_transactionsy(wallet, tron_address)
    #asyncio.create_task(catch_transactionsy(wallet, address_to))

    '''url = f"https://api.trongrid.io/v1/accounts/{address_to}/transactions?only_confirmed=true&only_to=true"

    response = requests.get(url, headers={"TRON-PRO-API-KEY": "5c4c149e-83d1-4926-8d73-78dac1ab2d38"})

    if response.status_code == 200:
        total = 0
        transactions = json.loads(response.text)["data"]
        for tx in transactions:
            if tx["raw_data"]["contract"][0]["parameter"]["value"]["to_address"] == address_to and tx["raw_data"]["contract"][0]["parameter"]["value"]["amount"] > 0:
                #if tx["raw_data"]["contract"][0]["parameter"]["value"]["owner_address"] == address_from:
                total += tx["raw_data"]["contract"][0]["parameter"]["value"]["amount"]
                print(tx["raw_data"]["contract"], total)'''

    #asyncio.create_task(catch_transactions20m(address_from, address_to))
    #total_amount = await catch_transactions20m(address_from, address_to)
    if type_net == "USDT":
        coinprice = GetUSDTPrice()
    elif type_net == "BTCB":
        coinprice = GetBtcPrice()
    elif type_net == "TRX":
        coinprice = GetTronPrice()

    qpay_amount, receipt = await check_trx_now(address_from, st, address_to) #, pay_status, receipt
    print(qpay_amount, coinprice)
    if qpay_amount > 0:
        pay_amount = qpay_amount*int(float(coinprice))/1000000
    elif qpay_amount == 0:
        pay_amount = int(float(coinprice))/1000000
    print(pay_amount)
    get_user = get_userx(user_id=call.from_user.id)

    #if pay_status == "SUCCESS":
    if qpay_amount > 0:
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, get_way)
        else:
            await call.answer("❗ Ваше пополнение уже было зачислено.", True)
        '''elif pay_status == "EXPIRED":
            await call.message.edit_text(_("<b>❌ Время оплаты вышло. Платёж был удалён.</b>", locale=lang))
        elif pay_status == "WAITING":
            await call.answer(_("❗ Платёж не был найден.\n"
                                "⌛ Попробуйте чуть позже.", locale=lang), True, cache_time=5)
        elif pay_status == "REJECTED":
            await call.message.edit_text(_("<b>❌ Счёт был отклонён.</b>", locale=lang))'''
    else:
        await call.message.edit_text(f"<b>❌ Транзакция не найдена, если вы выполнили перевод, попробуйте проверить позже.</b>")

# Проверка оплаты через сеть TronNet
@dp.callback_query_handler(text_contains="Pay:BTCB", state="*")  #text_contains text_startswith
async def refill_check_tron(call: CallbackQuery, state: FSMContext):
    print("UT 320")
    get_way = call.data.split(":")[1]
    type_net = call.data.split(":")[2]
    receipt = call.data.split(":")[3]
    user_id = call.from_user.id
    print(type_net, receipt)

    await state.update_data(here_type_net=type_net)
    await call.answer(f"♻ Подождите, платёж проверяется...")

    #address_to = 'TQanL97TYygHiycDZ1up8XNqt1mHcGJ4Nv'
    #address_to = '0x9798e988664856c20c37b5bf311a4ee85227a0df'
    address_to = get_system_crypto_address(get_way)['tron_address']

    address_from = (await state.get_data())['here_crypto_address']
    print(address_to, address_from)
    st = get_unix()

    if type_net == "USDT":
        coinprice = GetUSDTPrice()
    elif type_net == "BTCB":
        coinprice = GetBtcPrice()
    elif type_net == "TRX":
        coinprice = GetTronPrice()

    qpay_amount, receipt = await check_btc_now(address_from, st, address_to)
    print(qpay_amount, coinprice)
    if qpay_amount > 0:
        pay_amount = round((qpay_amount / 1000000000000000000 * float(coinprice)), 2)
        #pay_amount = qpay_amount*int(float(coinprice))/1000000/1000000/10000000
    elif qpay_amount == 0:
        pay_amount = int(float(coinprice))/1000000
    print(pay_amount)
    get_user = get_userx(user_id=call.from_user.id)

    #if pay_status == "SUCCESS":
    if qpay_amount > 0:
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, get_way)
        else:
            await call.message.edit_text("❗ Ваше пополнение уже было зачислено.")
        '''elif pay_status == "EXPIRED":
            await call.message.edit_text(_("<b>❌ Время оплаты вышло. Платёж был удалён.</b>", locale=lang))
        elif pay_status == "WAITING":
            await call.answer(_("❗ Платёж не был найден.\n"
                                "⌛ Попробуйте чуть позже.", locale=lang), True, cache_time=5)
        elif pay_status == "REJECTED":
            await call.message.edit_text(_("<b>❌ Счёт был отклонён.</b>", locale=lang))'''
    else:
        await call.message.edit_text(f"<b>❌ Транзакция не найдена, если вы выполнили перевод, попробуйте проверить позже.</b>")


# Принятие Трон адреса и сохранение если нет
@dp.message_handler(state="here_tron_address")
async def enter_tron_address(message: Message, state: FSMContext):
    user_id = message.from_user.id
    type_net = "USDT"
    trx_address = ""
    print("PPPP")

    if message.text:
        tron_address = message.text
        if tron_address == "" or tron_address is None:
            await message.answer(f"<b>♻ Был введен пустой адрес</b>", reply_markup=back_to_profile_finl())

        trx_address = get_crypto_address(user_id, tron_address)

        if trx_address:
            create_crypto_payment_row(user_id, tron_address, type_net)
        else:
            update_crypto_address(user_id, tron_address=tron_address, type_net=type_net)

        await state.update_data(here_tron_address=tron_address)
        await state.set_state("here_pay_amount")

        await message.answer(f"<b>♻ Успешно сохранили Ваш Crypto адрес в профиле.</b>", reply_markup=back_to_profile_finl())


# Принятие Трон адреса и сохранение если нет
@dp.message_handler(state="here_crypto_address")
async def enter_tron_address(message: Message, state: FSMContext):
    user_id = message.from_user.id
    type_net = (await state.get_data())['here_type_net']

    if message.text:
        crypto_address = message.text

        trx_address = get_crypto_address(user_id, crypto_address)
        #print(trx_address)
        if trx_address:
            create_crypto_payment_row(user_id, crypto_address, type_net)
        else:
            update_crypto_address(user_id, tron_address=crypto_address, type_net=type_net)

        create_crypto_payment_row(user_id, crypto_address, type_net)

        await state.update_data(here_crypto_address=crypto_address)
        await state.set_state("here_pay_amount")

        await message.answer(f"<b>♻ Успешно сохранили Ваш Crypto адрес в профиле.</b>", reply_markup=back_to_profile_finl())


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
