# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline_user import user_support_finl
from tgbot.keyboards.reply_z_all import menu_frep
from tgbot.loader import dp
from tgbot.services.api_sqlite import get_settingsx, get_userx
from tgbot.utils.misc.bot_filters import IsBuy, IsRefill, IsWork
from tgbot.utils.misc_functions import get_position_of_day
from tgbot.services.location_function import is_location
from tgbot.services.location_stat import geo_choice
from tgbot.keyboards.location_keyboards import geo_11_kb

#from tgbot.services.user_seller_function import is_seller
#from tgbot.keyboards.user_seller_keyboards import geo_1_kb

# Игнор-колбэки покупок
prohibit_buy = ['buy_category_open', 'buy_category_return', 'buy_category_nextp', 'buy_category_backp',
                'buy_shop_open', 'buy_shop_return', 'buy_shop_nextp', 'buy_shop_backp',
                'buy_position_open', 'buy_position_open', 'buy_position_return', 'buy_position_nextp', 'buy_position_backp',
                'buy_purchase_select', 'here_purchase_count', 'xpurchase_item', 'add_item_cart', 'user_cart',
                'enter_address_manualy', 'enter_address_manualy_fin', 'checkout_finally',
                'here_itemsadd_cart', 'xaddcart_item', 'geo_first_letter', 'cart_checkout_start',
                'enter_message_manualy', 'conf_order_addr_saved']
#'add_item_cart', 'enter_address_manualy', 'enter_address_manualy_fin',
# Игнор-колбэки пополнений
prohibit_refill = ['user_refill', 'refill_choice', 'Pay:', 'Pay:Form', 'Pay:ForYm', 'Pay:Number', 'Pay:Nickname']


####################################################################################################
######################################## ТЕХНИЧЕСКИЕ РАБОТЫ ########################################
# Фильтр на технические работы - сообщение
@dp.message_handler(IsWork(), state="*")
async def filter_work_message(message: Message, state: FSMContext):
    await state.finish()

    user_support = get_settingsx()['misc_support']
    if str(user_support).isdigit():
        get_user = get_userx(user_id=user_support)

        if len(get_user['user_login']) >= 1:
            await message.answer("<b>⛔ Бот находится на технических работах.</b>",
                                 reply_markup=user_support_finl(get_user['user_login']))
            return

    await message.answer("<b>⛔ Бот находится на технических работах.</b>")


# Фильтр на технические работы - колбэк
@dp.callback_query_handler(IsWork(), state="*")
async def filter_work_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Бот находится на технических работах.", True)


####################################################################################################
########################################### СТАТУС ПОКУПОК #########################################
# Фильтр на доступность покупок - сообщение
@dp.message_handler(IsBuy(), text="🎁 Купить", state="*")
@dp.message_handler(IsBuy(), state="here_purchase_count")
async def filter_buy_message(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⛔ Покупки временно отключены.</b>")

# Фильтр на доступность покупок - колбэк
@dp.callback_query_handler(IsBuy(), text_startswith=prohibit_buy, state="*")
async def filter_buy_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Покупки временно отключены.", True)


####################################################################################################
######################################### СТАТУС ПОПОЛНЕНИЙ ########################################
# Фильтр на доступность пополнения - сообщение
@dp.message_handler(IsRefill(), state="here_pay_amount")
async def filter_refill_message(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⛔ Пополнение временно отключено.</b>")


# Фильтр на доступность пополнения - колбэк
@dp.callback_query_handler(IsRefill(), text_startswith=prohibit_refill, state="*")
async def filter_refill_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Пополнение временно отключено.", True)


####################################################################################################
############################################## ПРОЧЕЕ ##############################################
# Открытие главного меню
@dp.message_handler(text=['⬅ Главное меню', '/start', '⬆️ Выбрать город позже'], state="*")
async def main_start(message: Message, state: FSMContext):
    await state.finish()

    get_settings = get_settingsx()
    type_trade = get_settings['type_trade']

    if type_trade == 'hybrid' or type_trade == 'real':
        if message.text == '⬆️ Выбрать город позже':
            await message.answer("🔸 Бот готов к использованию.\n"
                                 "🔸 Если не появились вспомогательные кнопки\n"
                                 "▶ Введите /start",
                                 reply_markup=menu_frep(message.from_user.id))

        else:
            if is_location(message.from_user.id) == True:

                await message.answer("🔸 Бот готов к использованию.\n"
                                     "🔸 Если не появились вспомогательные кнопки\n"
                                     "▶ Введите /start",
                                     reply_markup=menu_frep(message.from_user.id))
            else:
                await geo_choice.location.set()
                await message.answer('Отправьте локацию или выберите город из списка', reply_markup=geo_11_kb())

    elif type_trade == 'digital':
        await message.answer("🔸 Бот готов к использованию.\n"
                             "🔸 Если не появились вспомогательные кнопки\n"
                             "▶ Введите /start",
                             reply_markup=menu_frep(message.from_user.id))
