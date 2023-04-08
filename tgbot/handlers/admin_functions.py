# - *- coding: utf- 8 - *-
import asyncio
import gettext
from pathlib import Path
from contextvars import ContextVar

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import CantParseEntities

from babel import Locale
from tgbot.data.config import get_admins, BOT_DESCRIPTION, I18N_DOMAIN, LOCALES_DIR
#from tgbot.middlewares.i18n import I18nMiddleware
#from aiogram.contrib.middlewares.i18n import I18nMiddleware
from tgbot.middlewares.i18n import I18nMiddleware

from tgbot.keyboards.inline_admin import profile_search_finl, profile_search_reqs_finl
from tgbot.keyboards.inline_z_all import ad_confirm_inl, ad_add_to_plan_inl
from tgbot.loader import dp, bot
from tgbot.services.api_sqlite import *
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.utils.misc_functions import open_profile_search, open_profile_search_req, upload_text, generate_sales_report, open_profile_search_seller
#from munch import Munch

i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
print(i18n)
_ = i18n.gettext

# Рассылка PRO
@dp.message_handler(text=["📢 Рассылка", "📢 Mass Send"], state="*")
async def functions_ad(message: Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    user_role = get_userx(user_id=user_id)['user_role']
    lang = get_userx(user_id=user_id)['user_lang']
    print(lang)
    if user_role in ['Admin', 'ShopAdmin']:
        await state.set_state("here_ad_post")
        await message.answer(_("<b>📢 Введите текст для рассылки пользователям</b>", locale=lang))

######################################## ПРИНЯТИЕ ДАННЫХ ########################################
# Принятие текста для рассылки
@dp.message_handler(IsAdmin(), state="here_ad_post", content_types=types.ContentType.ANY)
async def functions_ad_get(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)
    get_users = get_all_usersx()
    user_id = message.from_user.id
    #lang = get_userx(user_id=user_id)['user_lang']
    mode = "tohour"

    if types.ContentType.TEXT == message.content_type:
        ct = 'text'
        await state.update_data(ct='text', here_ad_post=str(message.html_text))
        add_post_to_plan(ct, user_id, message.html_text, mode, caption='')
    elif types.ContentType.PHOTO == message.content_type:
        ct = 'photo'
        caption=message.html_text if message.caption else None
        await state.update_data(ct="photo", here_ad_photo=message.photo[-1].file_id, caption=caption)
        add_post_to_plan(ct, user_id, message.photo[-1].file_id, mode, caption=caption)
    elif types.ContentType.VIDEO == message.content_type:
        ct = 'video'
        caption=message.html_text if message.caption else None
        await state.update_data(ct="video", here_ad_video=message.video.file_id, caption=caption)
        add_post_to_plan(ct, user_id, message.video[-1].file_id, mode, caption=caption)
    elif types.ContentType.ANIMATION == message.content_type:
        ct = 'animation'
        caption=message.html_text if message.caption else None
        await state.update_data(ct="animation", here_ad_animation=message.animation.file_id, caption=caption)
        add_post_to_plan(ct, user_id, message.animation[-1].file_id, mode, caption=caption)
    post_id = get_lastpost()

    print(post_id)

    try:
        cache_msg = await message.answer(f"Тип поста:{ct}")
        await state.update_data(post_id=post_id)
        print(post_id)
        user_id = message.from_user.id
        lang = get_userx(user_id=user_id)['user_lang']
        print(lang)
        await message.answer(_("<b>📢 Включить пост в ротацию бота?</b>", locale=lang),
            reply_markup=ad_add_to_plan_inl,
            disable_web_page_preview=True
        )
    except CantParseEntities:
        await message.answer(_("<b>❌ Ошибка синтаксиса HTML.</b>\n"
                             "📢 Введите текст для рассылки пользователям.\n"
                             "❕ Вы можете использовать HTML разметку.", locale=lang))


# Подтверждение отправки рассылки
@dp.callback_query_handler(IsAdmin(), text_startswith="plan_once_ad", state="*")
async def functions_ad_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    get_users = get_all_usersx()
    user_id = call.from_user.id
    lang = get_userx(user_id=user_id)['user_lang']
    post_id = (await state.get_data())['post_id']
    ct = (await state.get_data())['ct']

    try:
        if get_action == "yes":

            cache_msg = await call.message.answer(f"Выбрано добавление в план:{ct}")
            await cache_msg.delete()

        await state.set_state("here_ad_post_confirm")
        post = get_postx(post_id)
        print(post)

        await call.message.answer(f"<b>📢 Отправить <code>{len(get_users)}</code> юзерам сообщение?</b>\n",
            reply_markup=ad_confirm_inl,
            disable_web_page_preview=True
        )
    except CantParseEntities:
        await message.answer(_("<b>❌ Ошибка синтаксиса HTML.</b>\n"
                             "📢 Введите текст для рассылки пользователям.\n"
                             "❕ Вы можете использовать HTML разметку.", locale=lang))

# Подтверждение отправки рассылки
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_ad", state="here_ad_post_confirm")
async def functions_ad_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    user_id = call.from_user.id
    lang = get_userx(user_id=user_id)['user_lang']
    ct = (await state.get_data())['ct']
    mode = "evening"
    if ct == "text":
        #print("|")
        send_message = (await state.get_data())['here_ad_post']
    elif ct == "photo":
        #print("||")
        send_photo = (await state.get_data())['here_ad_photo']
        caption = (await state.get_data())['caption']
    elif ct == "video":
        #print("|||")
        send_video = (await state.get_data())['here_ad_video']
        caption = (await state.get_data())['caption']
    elif ct == "animation":
        #print("||||")
        send_animation = (await state.get_data())['here_ad_animation']
        caption = (await state.get_data())['caption']

    get_users = get_all_usersx()
    await state.finish()

    if get_action == "yes":
        await call.message.edit_text(f"<b>📢 Рассылка началась... (0/{len(get_users)})</b>")
        if ct == "text":
            asyncio.create_task(functions_adext_make(ct, send_message, 0, call))
        if ct == "photo":
            asyncio.create_task(functions_adext_make(ct, send_photo, caption, call))
        if ct == "video":
            asyncio.create_task(functions_adext_make(ct, send_video, caption, call))
        if ct == "animation":
            asyncio.create_task(functions_adext_make(ct, send_animation, caption, call))
    else:
        await call.message.edit_text(_("<b>📢 Вы отменили отправку рассылки ✅</b>", locale=lang))


# Поиск профиля
@dp.message_handler(IsAdmin(), text=["👤 Поиск профиля 🔍", "👤 Find Profile 🔍"], state="*")
async def functions_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_userx(user_id=user_id)['user_lang']
    await state.finish()

    await state.set_state("here_profile")
    await message.answer(_("<b>👤 Введите логин или айди пользователя</b>", locale=lang))

# Поиск чеков
@dp.message_handler(IsAdmin(), text=["🧾 Поиск чеков 🔍", "🧾 Find Receipts 🔍"], state="*")
async def functions_receipt(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_userx(user_id=user_id)['user_lang']
    await state.finish()

    await state.set_state("here_receipt")
    await message.answer(_("<b>🧾 Отправьте номер чека</b>", locale=lang))

# Просмотр запросов продавцов
@dp.message_handler(text=["🖍 Посмотреть запросы", "🖍 Show list requests"], state="*")
async def functions_seller_requests(message: Message, state: FSMContext):

    user_id = message.from_user.id
    user_role = get_userx(user_id=user_id)['user_role']
    lang = get_userx(user_id=user_id)['user_lang']
    print(lang)
    if user_role in ['Admin', 'ShopAdmin']:
        await message.answer(_("<b>🧾 Посмотрим запросы продавцов:</b>", locale=lang))

    all_requests = get_all_requestx()
    if len(all_requests) >= 1:
        await message.answer(_("Запросы на роль продавца:", locale=lang) + str(len(all_requests)) + "шт.")

        for request in all_requests:
            print(request)
            await state.finish()
            await message.answer(open_profile_search_req(request['user_id'], lang), reply_markup=profile_search_reqs_finl(request['user_id'], lang))


# Просмотр запросов продавцов
@dp.message_handler(IsAdmin(), text=["📊 Отчет о продажах", "📊 Sales Report"], state="*")
async def functions_seller_requests(message: Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    user_role = get_userx(user_id=user_id)['user_role']
    lang = get_userx(user_id=user_id)['user_lang']

    await message.answer(generate_sales_report())

    get_users = get_purchasesbysellers()

    if len(get_users)>= 1:
        await message.answer(_("Топ - продавцов", locale=lang) + str(get_users) + _("шт.", locale=lang))

        for user in get_users:

            await message.answer(open_profile_search_seller(user_id=user['user_id']), reply_markup=profile_search_finl(user['user_id']))

########################################### CALLBACKS ###########################################
# Подтверждение отправки рассылки
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_ad", state="here_ad_confirm")
async def functions_ad_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    user_id = call.from_user.id
    lang = get_userx(user_id=user_id)['user_lang']

    send_message = (await state.get_data())['here_ad_text']
    get_users = get_all_usersx()
    await state.finish()

    if get_action == "yes":
        await call.message.edit_text(_("<b>📢 Рассылка началась... (0/", locale=lang) + len(get_users) + _(")</b>", locale=lang))
        asyncio.create_task(functions_ad_make(send_message, call))
    else:
        await call.message.edit_text(_("<b>📢 Вы отменили отправку рассылки ✅</b>", locale=lang))


# Покупки пользователя
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_purchases", state="*")
async def functions_profile_purchases(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    lang = get_userx(user_id=user_id)['user_lang']
    last_purchases = last_purchasesx(user_id, 10)

    if len(last_purchases) >= 1:
        await call.answer(_("🎁 Последние 10 покупок", locale=lang))
        await call.message.delete()

        for purchases in last_purchases:
            link_items = await upload_text(call, purchases['purchase_item'])
            if lang == "ru":
                await call.message.answer(f"<b>🧾 Чек: <code>#{purchases['purchase_receipt']}</code></b>\n"
                                          f"🎁 Товар: <code>{purchases['purchase_position_name']} | {purchases['purchase_count']}шт | {purchases['purchase_price']}₽</code>\n"
                                          f"🕰 Дата покупки: <code>{purchases['purchase_date']}</code>\n"
                                          f"🔗 Товары: <a href='{link_items}'>кликабельно</a>")
            if lang == "en":
                await call.message.answer(f"<b>🧾 Receipt: <code>#{purchases['purchase_receipt']}</code></b>\n"
                                          f"🎁 Product: <code>{purchases['purchase_position_name']} | {purchases['purchase_count']}pcs | {purchases['purchase_price']}₽</code>\n"
                                          f"🕰 Purchase Date: <code>{purchases['purchase_date']}</code>\n"
                                          f"🔗 Products: <a href='{link_items}'>clickable</a>")

        await call.message.answer(open_profile_search(user_id), reply_markup=profile_search_finl(user_id))
    else:
        if lang == "ru":
            await call.answer("❗ У пользователя отсутствуют покупки", True)
        if lang == "en":
            await call.answer("❗ User don't have purchases", True)


# Отправка рассылки
async def functions_adext_make(ct, message, caption, call: CallbackQuery):
    receive_users, block_users, how_users = 0, 0, 0
    get_users = get_all_usersx()
    #user_id = call.data.split(":")[1]
    user_id = call.from_user.id
    lang = get_userx(user_id=user_id)['user_lang']

    for user in get_users:
        try:
            if ct == "text":
                await dp.bot.send_message(user['user_id'], message, disable_web_page_preview=True)
            elif ct == "photo":
                await dp.bot.send_photo(
                    chat_id=user['user_id'],
                    photo=message,
                    caption=caption or None,
                )
            elif ct == "video":
                await dp.bot.send_video(
                    chat_id=user['user_id'],
                    video=message,
                    caption=caption or None,
                )
            elif ct == "animation":
                await dp.bot.send_animation(
                    chat_id=user['user_id'],
                    animation=message,
                    caption=caption or None,
                )

            receive_users += 1
        except Exception:
            block_users += 1

        how_users += 1

        if how_users % 10 == 0:
            await call.message.edit_text("<b>📢 Рассылка началась... (" + str(how_users) + "/" + str(len(get_users)) + ")</b>")
        #_("<b>📢 Рассылка началась... (", locale=lang)
        await asyncio.sleep(0.05)

    if lang == "ru":
        await call.message.edit_text(
            f"<b>📢 Рассылка была завершена ✅</b>\n"
            f"👤 Пользователей получило сообщение: <code>{receive_users} ✅</code>\n"
            f"👤 Пользователей не получило сообщение: <code>{block_users} ❌</code>"
        )
    if lang == "en":
        await call.message.edit_text(
            f"<b>📢 Mass Sending has been finished ✅</b>\n"
            f"👤 Users Received Messages: <code>{receive_users} ✅</code>\n"
            f"👤 Users not Received Messages: <code>{block_users} ❌</code>"
        )

# Отправка рассылки
async def functions_ad_make(message, call: CallbackQuery):
    receive_users, block_users, how_users = 0, 0, 0
    get_users = get_all_usersx()

    for user in get_users:
        try:
            await bot.send_message(user['user_id'], message, disable_web_page_preview=True)
            receive_users += 1
        except Exception:
            block_users += 1

        how_users += 1

        if how_users % 10 == 0:
            await call.message.edit_text(_("<b>📢 Рассылка началась... (", locale=lang) + str(how_users) + "/" + str(len(get_users)) + "</b>")
        #_("<b>📢 Рассылка началась... (", locale=lang)
        await asyncio.sleep(0.05)

    await call.message.edit_text(
        f"<b>📢 Рассылка была завершена ✅</b>\n"
        f"👤 Пользователей получило сообщение: <code>{receive_users} ✅</code>\n"
        f"👤 Пользователей не получило сообщение: <code>{block_users} ❌</code>"
    )

# Подтверждение запроса продавца
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_request_approve", state="*")
async def functions_shopadmin_request_approve(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    get_user = get_userx(user_id=user_id)
    update_userx(user_id, user_role="ShopAdmin")
    update_requestx(user_id, state="Approved")

    await state.finish()
    await call.message.answer(
        f"<b>✅ Пользователю <a href='tg://user?id={user_id}'>{get_user['user_name']}</a> "
        f"изменена роль на: <code>{get_user['user_role']}</code></b>")

    await bot.send_message(user_id, "<b> Вам была выдана роль Продавца магазина. </b>")


# Отклонение запроса продавца
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_request_decline", state="*")
async def functions_shopadmin_request_decline(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = call.data.split(":")[1]
    print(user_id)
    delete_requests_userx(user_id)

    await call.answer(_(" Запрос был успешно удален.", locale=lang))

    await bot.send_message(
        user_id,
        _("<b>Ваш запрос был отклонен. Вы можете попробовать подать следующий запрос через 14 дней.</b>",
            locale=lang,
        ),
    )


# Выдача баланса пользователю
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_balance_add", state="*")
async def functions_profile_balance_add(call: CallbackQuery, state: FSMContext):
    await state.update_data(here_profile=call.data.split(":")[1])
    auser_id = call.from_user.id
    lang, user_role = get_userx(user_id=auser_id)['user_lang'], get_userx(user_id=auser_id)['user_role']

    await state.set_state("here_profile_add")
    await call.message.edit_text(_("<b>💰 Введите сумму для выдачи баланса</b>", locale=lang))


# Изменение баланса пользователю
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_balance_set", state="*")
async def functions_profile_balance_set(call: CallbackQuery, state: FSMContext):
    await state.update_data(here_profile=call.data.split(":")[1])
    auser_id = call.from_user.id
    lang, user_role = get_userx(user_id=auser_id)['user_lang'], get_userx(user_id=auser_id)['user_role']

    await state.set_state("here_profile_set")
    await call.message.edit_text(_("<b>💰 Введите сумму для изменения баланса</b>", locale=lang))


# Обновление профиля пользователя
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_refresh", state="*")
async def functions_profile_refresh(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    auser_id = call.from_user.id
    lang, user_role = get_userx(user_id=auser_id)['user_lang'], get_userx(user_id=auser_id)['user_role']

    await call.message.delete()
    await call.message.answer(open_profile_search(user_id, lang), reply_markup=profile_search_finl(user_id))


######################################## СМЕНА СТАТУСОВ ПОЛЬЗОВАТЕЛЯ ############################

# Принятие суммы для выдачи баланса пользователю
@dp.callback_query_handler(IsAdmin(), state="here_user_request_approve")
async def functions_shopadmin_request_approvep(message: Message, state: FSMContext):
    user_id = (await state.get_data())['here_profile']
    await state.finish()

    get_user = get_userx(user_id=user_id)
    update_userx(user_id, user_role="ShopAdmin")
    lang = get_user(user_id=user_id)['user_lang']

    await message.answer(
        f"<b>✅ Пользователю <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> "
        f"изменена роль на: <code>{get_user['user_role']}</code></b>")

    await message.bot.send_message(
        user_id,
        _("<b> Вам была выдана роль Продавца магазина </b>", locale=lang),
    )
    await message.answer(open_profile_search(user_id), reply_markup=profile_search_finl(user_id))


######################################## ПРИНЯТИЕ ДАННЫХ ########################################
# Принятие текста для рассылки
@dp.message_handler(IsAdmin(), state="here_ad_text")
async def functions_ad_get(message: Message, state: FSMContext):
    await state.update_data(here_ad_text="📢 Рассылка.\n" + str(message.text))
    get_users = get_all_usersx()

    try:
        cache_msg = await message.answer(message.text)
        await cache_msg.delete()

        await state.set_state("here_ad_confirm")
        await message.answer(
            f"<b>📢 Отправить <code>{len(get_users)}</code> юзерам сообщение?</b>\n"
            f"{message.text}",
            reply_markup=ad_confirm_inl,
            disable_web_page_preview=True
        )
    except CantParseEntities:
        await message.answer(_("<b>❌ Ошибка синтаксиса HTML.</b>\n"
                             "📢 Введите текст для рассылки пользователям.\n"
                             "❕ Вы можете использовать HTML разметку.", locale=lang))

# Принятие айди или логина для поиска профиля
@dp.message_handler(IsAdmin(), state="here_profile")
async def functions_profile_get(message: Message, state: FSMContext):
    find_user = message.text
    auser_id = message.from_user.id
    lang, user_role = get_user(user_id=auser_id)['user_lang'], get_user(user_id=auser_id)['user_role']

    if find_user.isdigit():
        get_user = get_userx(user_id=find_user)
    else:
        if find_user.startswith("@"): find_user = find_user[1:]
        print(find_user)
        get_user = get_userx(user_login=find_user.lower())

    if get_user is not None:
        await state.finish()
        await message.answer(open_profile_search(get_user['user_id'], lang),
                             reply_markup=profile_search_finl(get_user['user_id'], lang))
    else:
        await message.answer(_("<b>❌ Профиль не был найден</b>"
                             "👤 Введите логин или айди пользователя.", locale=lang))


# Принятие суммы для выдачи баланса пользователю
@dp.message_handler(IsAdmin(), state="here_profile_add")
async def functions_profile_balance_add_get(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 1000000000:
            user_id = (await state.get_data())['here_profile']
            await state.finish()

            get_user = get_userx(user_id=user_id)
            update_userx(user_id, user_balance=get_user['user_balance'] + int(message.text))

            await message.answer(
                f"<b>✅ Пользователю <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> "
                f"выдано <code>{message.text}₽</code></b>")

            await message.bot.send_message(user_id, f"<b>💰 Вам было выдано <code>{message.text}₽</code></b>")
            await message.answer(open_profile_search(user_id), reply_markup=profile_search_finl(user_id))
        else:
            await message.answer(_("<b>❌ Сумма выдачи не может быть меньше 1 и больше 1 000 000 000</b>\n"
                                 "💰 Введите сумму для выдачи баланса", locale=lang))
    else:
        await message.answer(_("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для выдачи баланса", locale=lang))


# Принятие суммы для изменения баланса пользователя
@dp.message_handler(IsAdmin(), state="here_profile_set")
async def functions_profile_balance_set_get(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 1000000000:
            user_id = (await state.get_data())['here_profile']
            await state.finish()

            get_user = get_userx(user_id=user_id)
            update_userx(user_id, user_balance=message.text)

            await message.answer(
                f"<b>✅ Пользователю <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> "
                f"изменён баланс на <code>{message.text}₽</code></b>")

            await message.answer(open_profile_search(user_id), reply_markup=profile_search_finl(user_id))
        else:
            await message.answer(_("<b>❌ Сумма изменения не может быть меньше 0 и больше 1 000 000 000</b>\n"
                                 "💰 Введите сумму для изменения баланса", locale=lang))
    else:
        await message.answer(_("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для изменения баланса", locale=lang))


# Отправка сообщения пользователю
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_message", state="*")
async def functions_profile_user_message(call: CallbackQuery, state: FSMContext):
    await state.update_data(here_profile=call.data.split(":")[1])

    await state.set_state("here_profile_message")
    await call.message.edit_text(_("<b>💌 Введите сообщение для отправки</b>\n"
                                 "⚠ Сообщение будет сразу отправлено пользователю."), locale=lang)

# Принятие сообщения для пользователя
@dp.message_handler(IsAdmin(), state="here_profile_message")
async def functions_profile_user_message_get(message: Message, state: FSMContext):
    user_id = (await state.get_data())['here_profile']
    auser_id = message.from_user.id
    lang = get_userx(user_id=auser_id)['user_lang']
    await state.finish()

    get_message = _("<b>💌 Вам сообщение:</b>", locale=lang) + clear_html(message.text)
    get_user = get_userx(user_id=user_id)

    await message.bot.send_message(user_id, get_message)
    await message.answer(_("<b>✅ Пользователю ", locale=lang) + f"<a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> "
                         + _("было отправлено сообщение:</b>", locale=lang) +
                         f"{get_message}")

    await message.answer(open_profile_search(user_id), reply_markup=profile_search_finl(user_id))


# Принятие чека для поиска
@dp.message_handler(IsAdmin(), state="here_receipt")
async def functions_receipt_search(message: Message, state: FSMContext):
    receipt = message.text[1:]
    get_refill = ""
    user_id = message.from_user.id
    lang = get_userx(user_id=user_id)['user_lang']

    if message.text.startswith("#"):
        get_refill = get_refillx(refill_receipt=receipt)
        get_purchase = get_purchasex(purchase_receipt=receipt)

        if get_refill is not None:
            await state.finish()

            if get_refill['refill_way'] == "Form":
                way_input = _("🥝 Способ пополнения: <code>По форме</code>", locale=lang)
            elif get_refill['refill_way'] == "Nickname":
                way_input = _("🥝 Способ пополнения: <code>По никнейму</code>", locale=lang)
            elif get_refill['refill_way'] == "Number":
                way_input = _("🥝 Способ пополнения: <code>По номеру</code>", locale=lang)
            else:
                way_input = _(f"🥝 Способ пополнения: <code>{get_refill['refill_way']}</code>", locale=lang)

            if lang == "ru":
                await message.answer(
                    f"<b>🧾 Чек: <code>#{get_refill['refill_receipt']}</code></b>\n"
                    "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"👤 Пользователь: <a href='tg://user?id={get_refill['user_id']}'>{get_refill['user_name']}</a> <code>({get_refill['user_id']})</code>\n"
                    f"💰 Сумма пополнения: <code>{get_refill['refill_amount']}₽</code>\n"
                    f"{way_input}\n"
                    f"🏷 Комментарий: <code>{get_refill['refill_comment']}</code>\n"
                    f"🕰 Дата пополнения: <code>{get_refill['refill_date']}</code>"
                )
            if lang == "en":
                await message.answer(
                    f"<b>🧾 Receipt: <code>#{get_refill['refill_receipt']}</code></b>\n"
                    "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"👤 User: <a href='tg://user?id={get_refill['user_id']}'>{get_refill['user_name']}</a> <code>({get_refill['user_id']})</code>\n"
                    f"💰 Charge Amount: <code>{get_refill['refill_amount']}₽</code>\n"
                    f"{way_input}\n"
                    f"🏷 Comment: <code>{get_refill['refill_comment']}</code>\n"
                    f"🕰 Date of charge: <code>{get_refill['refill_date']}</code>"
                )
            return
        elif get_purchase is not None:
            await state.finish()

            link_items = await upload_text(message, get_purchase['purchase_item'])
            if lang == "ru":
                await message.answer(
                    f"<b>🧾 Чек: <code>#{get_purchase['purchase_receipt']}</code></b>\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"👤 Пользователь: <a href='tg://user?id={get_purchase['user_id']}'>{get_purchase['user_name']}</a> <code>({get_purchase['user_id']})</code>\n"
                    f"🏷 Название товара: <code>{get_purchase['purchase_position_name']}</code>\n"
                    f"📦 Куплено товаров: <code>{get_purchase['purchase_count']}шт</code>\n"
                    f"💰 Цена 1-го товара: <code>{get_purchase['purchase_price_one']}₽</code>\n"
                    f"💸 Сумма покупки: <code>{get_purchase['purchase_price']}₽</code>\n"
                    f"🔗 Товары: <a href='{link_items}'>кликабельно</a>\n"
                    f"🔻 Баланс до покупки: <code>{get_purchase['balance_before']}₽</code>\n"
                    f"🔺 Баланс после покупки: <code>{get_purchase['balance_after']}₽</code>\n"
                    f"🕰 Дата покупки: <code>{get_purchase['purchase_date']}</code>"
                )
            if lang == "en":
                await message.answer(
                    f"<b>🧾 Receipt: <code>#{get_purchase['purchase_receipt']}</code></b>\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"👤 User: <a href='tg://user?id={get_purchase['user_id']}'>{get_purchase['user_name']}</a> <code>({get_purchase['user_id']})</code>\n"
                    f"🏷 Name of Product: <code>{get_purchase['purchase_position_name']}</code>\n"
                    f"📦 Products Purchased: <code>{get_purchase['purchase_count']}pcs</code>\n"
                    f"💰 Price for One Pieces: <code>{get_purchase['purchase_price_one']}R</code>\n"
                    f"💸 Summ of Purchaces: <code>{get_purchase['purchase_price']}R</code>\n"
                    f"🔗 Items: <a href='{link_items}'>кликабельно</a>\n"
                    f"🔻 Balance Before Purchase: <code>{get_purchase['balance_before']}R</code>\n"
                    f"🔺 Balance After Purchase: <code>{get_purchase['balance_after']}R</code>\n"
                    f"🕰 Purchase Date: <code>{get_purchase['purchase_date']}</code>"
                )

            return

    await message.answer(_("<b>❌ Чек не был найден.</b>\n"
                         "🧾 Отправьте номер чека", locale=lang))
