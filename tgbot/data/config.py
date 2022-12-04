# - *- coding: utf- 8 - *-
import sqlite3
import configparser
import json


read_config = configparser.ConfigParser()
read_config.read('settings.ini')

BOT_TOKEN = read_config['settings']['token'].strip()  # Токен бота
PATH_DATABASE = 'tgbot/data/database.db'  # Путь к БД
PATH_LOGS = 'tgbot/data/logs.log'  # Путь к Логам
BOT_VERSION = '1.0'

# Преобразование полученного списка в словарь


def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict

# Форматирование запроса без аргументов


def update_format(sql, parameters: dict):
    if "XXX" not in sql:
        sql += " XXX "

    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())


def get_type_trade():
    get_type_trade = get_settingsx()['type_trade']
    return get_type_trade

# Получение администраторов бота


def get_admins():
    read_admins = configparser.ConfigParser()
    read_admins.read('settings.ini')

    admins = read_admins['settings']['admin_id'].strip()
    admins = admins.replace(' ', '')

    if ',' in admins:
        admins = admins.split(',')
    else:
        if len(admins) >= 1:
            admins = [admins]
        else:
            admins = []

    while '' in admins:
        admins.remove('')
    while ' ' in admins:
        admins.remove(' ')
    while '\r' in admins:
        admins.remove('\r')

    admins = list(map(int, admins))
    # print(admins)
    return admins

    # Получение админов магазинов


def get_shopadmins():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT user_id FROM storage_users WHERE user_role='ShopAdmin'"
        allshopadmins = con.execute(sql).fetchall()
        # print(allshopadmins)
        shopadmins = []
        for admin in allshopadmins:
            k = admin['user_id']
            shopadmins.append(k)
        # print(shopadmins)
        # print(type(shopadmins))

    return shopadmins


def get_shopadmins2():
    read_shopadmins = configparser.ConfigParser()
    read_shopadmins.read('settings.ini')

    shopadmins = read_shopadmins['settings']['shopadmin_id'].strip()
    shopadmins = shopadmins.replace(' ', '')

    if ',' in shopadmins:
        shopadmins = shopadmins.split(',')
    else:
        if len(shopadmins) >= 1:
            shopadmins = [shopadmins]
        else:
            shopadmins = []

    while '' in shopadmins:
        shopadmins.remove('')
    while ' ' in shopadmins:
        shopadmins.remove(' ')
    while '\r' in shopadmins:
        shopadmins.remove('\r')

    shopadmins = list(map(int, shopadmins))

    return shopadmins

    # Получение админов магазинов


def is_shopadmin(user_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT user_id FROM storage_users "
        #sql, parameters = update_format(sql, kwargs)
        # parameters.append(user_id)
        shopadmin = con.execute(
            sql + "WHERE user_id = ?", [user_id]).fetchone()

    return shopadmin['user_id']


def check_adminproducts():
    #get_position = get_positionsx(position_user_id=message.from_user.id)

    return 1


BOT_DESCRIPTION = f"""
 
<b>❗🔴 Правила использования:</b>
- Запрещено менять данные аккаунта, при этом вы можете добавлять друзей (для того чтоб поиграть с ними)
- Запрещено использовать читы и другие виды мошенничества, играйте честно!
- Вы не можете передавать аккаунт третьему лицу. Если это произойдет, то у нас будет зафиксирован вход с другого устройства. Вы будете деавторизованы и лишены возможности зайти в аккаунт, без возврата денежных средств.
- На аккаунт может зайти наш оператор поддержки для проверки. При любых подозрениях, что аккаунтом кто-то пользуется кроме вас - сразу же сообщайте нам, мы проверим и деавторизуем любые сессии, кроме вашей.
- После истечения срока аренды вы не можете продолжать пользоваться аккаунтом и должны выйти из аккаунта или же оплатить дополнительное время аренды.

Активация предоставляется только на один компьютер. Вы платите за 1 активацию на 1 ПК!
✅ Обязательно проверьте что ваш компьютер соответствует минимальным требованиям игры!
✅ Мы не делаем возвратов если ваш ПК не соответствует минимальным требованиям игры.
✅ Аккаунт куплен легально, является собственностью продавца и не передается вам в собственность. Менять пароль ЗАПРЕЩЕНО! Вы получаете только право использования аккаунта.
➖➖➖➖➖➖➖➖➖➖
<b>⚜ Часто задаваемые вопросы:</b>
➖➖➖➖➖➖➖➖➖➖
<b>Как взять игру в аренду ?</b>
В главном меню бота выбираем - "Игры в аренду" => Игру которую хотите арендовать => Выбираете срок аренды =>
💰 Взять в аренду (Если на балансе недостаточно средств, пополнить баланс можно в профиле => "💰 Пополнить")

<b>Как я получу игру после оплаты ?</b>
Как только Вы оплатите аренду, доступы к аккаунту Steam появятся с Вашем профиле в разделе "🎁 Мои покупки"

<b>Как мне начать играть ?</b>
Вам выдаётся логин и пароль от аккаунта с игрой в Steam. 
Просто заходите в аккаунт с этими данными, на аккаунте будет арендованная игра. 
Срок аренды исчисляется с момента оплаты, устанавливаете и играете.

<b>Не могу войти в Steam, что делать?</b>
Если возникли сложности со входом, напишите нашему администратору - "@tech_steam"
Ответ вы получите в порядке очереди обращения.

<b>Могу ли я разместить свои игры в аренду в вашем магазине ?</b>
По вопросам сотрудничества пишите - @ru_adm

➖➖➖➖➖➖➖➖➖➖
<b>⚜ Контакты:</b>
Техническая поддержка : @tech_steam
Сотрудничество : @ru_adm
➖➖➖➖➖➖➖➖➖➖
""".strip()
