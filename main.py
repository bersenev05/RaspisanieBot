import asyncio
import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from user_base_worker import user_file
import json
from user_base_worker import add_base

# МАШИНА СОСТОЯНИЙ
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import api_main, api_statistics

# создаём бота
bot = Bot(token=api_main, parse_mode="HTML")

# подключаем диспетчера
dp = Dispatcher(bot, storage=MemoryStorage())

# создаём админ-панель(тоже бот, просто отдельный, будет присылать инфу админу)
statistic_bot = Bot(token=api_statistics, parse_mode="HTML")

# импортируем базу клиентов, там будем хранить всю инфу о них с помощью словарей
# username/ id/ cjm/ last_message/ kurs/ napravlenie/ group/ nedelya/ day
from user_base_worker import user_base
from user_base_worker import client_info
from config import admin


# функция для получения реального времени
from datetime import datetime

time = 0

async def get_time():
    global time
    time = datetime.now().strftime("%d.%m %H:%M:%S")

from new_worker import create_raspisanie
from new_worker import all_groups, all_raspisanie, create_timetable,create_oneday_timetable
from new_worker import groups_with_napr


# хендлер на команду /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # удаляем сообщение пользователя
    await message.delete()

    # инлайн клавиатура
    ikb = InlineKeyboardMarkup()
    for i in all_groups:
        ikb.row(InlineKeyboardButton(i+" курс", callback_data=i+"kurs"))
        kurs_handlers.append(i+"kurs")

    # отправляем приветственное сообщение
    msg = await message.answer("Привет! Я помогу тебе найти твоё расписание! На каком курсе ты учишься?",
                               reply_markup=ikb)

    # проверяем наличие клиента в базе. Если его там нет = добавляем
    if str(message.from_user.id) not in user_base or message.from_user.id in user_base:

        user_base[str(message.from_user.id)] = {
            "username": "@" + message.from_user.username,
            "id": message.from_user.id,
            "cjm": [],
            "last_message": msg.message_id
        }

    # получаем реальное время
    await get_time()

    # добавляем действие клиента в базу, сохраняем id последнего сообщения
    user_base[str(message.from_user.id)]["cjm"].append(f"{time} = <b>Вошёл в бота</b>")
    user_base[str(message.from_user.id)]["last_message"] = msg.message_id

    # получаем сводку о клиенте из user_base
    info = await client_info(message.from_user.id)

    #получаем все айди, юзернеймы, базу
    await user_file()
    media = types.MediaGroup()
    media.attach_document(types.InputFile('system_file.txt'))
    media.attach_document(types.InputFile('cjm_file.txt'))
    media.attach_document(types.InputFile('id_file.txt'))
    media.attach_document(types.InputFile('username_file.txt'),caption=f'<b>Новый пользователь</b>\n\n'
                                                                     f'{info}')

    # отправляем сводку всем админам
    for i in admin:
        await statistic_bot.send_media_group(chat_id=i,
                                             media=media)

kurs_handlers=[]
@dp.callback_query_handler(text=kurs_handlers)
async def kurs_handler(message: types.CallbackQuery):

    # получаем реальное время
    await get_time()

    # добавляем действие клиента в базу, сохраняем id последнего сообщения
    user_base[str(message.from_user.id)]["cjm"].append(f"{time} = <b>Нажал на {message.data} курс</b>")

    user_base[str(message.from_user.id)]["kurs"] = message.data[0]

    ikb = InlineKeyboardMarkup(row_width=2)
    for i in groups_with_napr[user_base[str(message.from_user.id)]["kurs"]]:
        ikb.insert(InlineKeyboardButton(i, callback_data=i))
        napravlenie_handlers.append(i)

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=user_base[str(message.from_user.id)]["last_message"],
                                text="Выбери своё направление",
                                reply_markup=ikb)

napravlenie_handlers=[]
@dp.callback_query_handler(text=napravlenie_handlers)
async def naprevlenie_handler(message: types.CallbackQuery):
    # получаем реальное время
    await get_time()

    # добавляем действие клиента в базу, сохраняем id последнего сообщения
    user_base[str(message.from_user.id)]["cjm"].append(f"{time} = <b>Нажал на {message.data}</b>")

    user_base[str(message.from_user.id)]["napravlenie"] = message.data

    ikb = InlineKeyboardMarkup(row_width=2)
    for i in groups_with_napr[user_base[str(message.from_user.id)]["kurs"]][message.data]:
        ikb.insert(InlineKeyboardButton(i, callback_data=i))
        group_handlers.append(i)

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=user_base[str(message.from_user.id)]["last_message"],
                                text="Выбери свою группу",
                                reply_markup=ikb)

group_handlers=[]
@dp.callback_query_handler(text=group_handlers)
async def group_handler(message: types.CallbackQuery):

    # получаем реальное время
    await get_time()
    # добавляем действие клиента в базу, сохраняем id последнего сообщения
    user_base[str(message.from_user.id)]["cjm"].append(f"{time} = <b>Нажал на {message.data}</b>")
    user_base[str(message.from_user.id)]["group"] = message.data
    user_base[str(message.from_user.id)]["nedelya"] = "Нечётная неделя"
    user_base[str(message.from_user.id)]["day"] = "Понедельник"

    user = user_base[str(message.from_user.id)]

    ikb=InlineKeyboardMarkup(row_width=3)
    days={"Понедельник":"пн",
          "Вторник":"вт",
          "Среда":"ср",
          "Четверг":"чт",
          "Пятницв":"пт",
          "Суббота":"сб"}

    for i in ["пн","вт","ср","чт","пт","сб"]:
        if i==days[user["day"]]:
            ikb.insert(InlineKeyboardButton("✅ "+i, callback_data=i))
        else:
            ikb.insert(InlineKeyboardButton(i, callback_data=i))

    if user["nedelya"] == "Чётная неделя":
        ikb.row(InlineKeyboardButton("🔄 Нечётная неделя",callback_data="change_week"))
    else:
        ikb.row(InlineKeyboardButton("🔄 Чётная неделя", callback_data="change_week"))

    ikb.row(InlineKeyboardButton("Поменять группу", callback_data="start"))


    msg = await create_oneday_timetable(user["kurs"], user['group'],user["nedelya"],user["day"])

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=user_base[str(message.from_user.id)]["last_message"],
                                text=f"{msg}",
                                reply_markup=ikb)

callback_days=["пн","вт","ср","чт","пт","сб"]
@dp.callback_query_handler(text=callback_days)
async def days_handler(message: types.CallbackQuery):

    if message.data=="пн":
        user_base[str(message.from_user.id)]["day"] = "Понедельник"
    elif message.data=="вт":
        user_base[str(message.from_user.id)]["day"] = "Вторник"
    elif message.data=="ср":
        user_base[str(message.from_user.id)]["day"] = "Среда"
    elif message.data=="чт":
        user_base[str(message.from_user.id)]["day"] = "Четверг"
    elif message.data=="пт":
        user_base[str(message.from_user.id)]["day"] = "Пятница"
    elif message.data=="сб":
        user_base[str(message.from_user.id)]["day"] = "Суббота"

    # получаем реальное время
    await get_time()
    # добавляем действие клиента в базу, сохраняем id последнего сообщения
    user_base[str(message.from_user.id)]["cjm"].append(f"{time} = <b>Нажал на {message.data}</b>")

    user = user_base[str(message.from_user.id)]

    ikb = InlineKeyboardMarkup(row_width=3)
    days = {"Понедельник": "пн",
            "Вторник": "вт",
            "Среда": "ср",
            "Четверг": "чт",
            "Пятница": "пт",
            "Суббота": "сб"}

    for i in ["пн", "вт", "ср", "чт", "пт", "сб"]:
        if i == days[user["day"]]:
            ikb.insert(InlineKeyboardButton("✅ " + i, callback_data=i))
        else:
            ikb.insert(InlineKeyboardButton(i, callback_data=i))

    if user["nedelya"] == "Чётная неделя":
        ikb.row(InlineKeyboardButton("🔄 Нечётная неделя",callback_data="change_week"))
    else:
        ikb.row(InlineKeyboardButton("🔄 Чётная неделя", callback_data="change_week"))

    ikb.row(InlineKeyboardButton("Поменять группу", callback_data="start"))

    msg = await create_oneday_timetable(user["kurs"], user['group'], user["nedelya"], user["day"])

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=user_base[str(message.from_user.id)]["last_message"],
                                text=f"{msg}",
                                reply_markup=ikb)

@dp.callback_query_handler(text="change_week")
async def days_handler(message: types.CallbackQuery):

    # получаем реальное время
    await get_time()
    # добавляем действие клиента в базу, сохраняем id последнего сообщения
    user_base[str(message.from_user.id)]["cjm"].append(f"{time} = <b>Нажал на {message.data}</b>")

    user = user_base[str(message.from_user.id)]

    ikb = InlineKeyboardMarkup(row_width=3)
    days = {"Понедельник": "пн",
            "Вторник": "вт",
            "Среда": "ср",
            "Четверг": "чт",
            "Пятница": "пт",
            "Суббота": "сб"}

    for i in ["пн", "вт", "ср", "чт", "пт", "сб"]:
        if i == days[user["day"]]:
            ikb.insert(InlineKeyboardButton("✅ " + i, callback_data=i))
        else:
            ikb.insert(InlineKeyboardButton(i, callback_data=i))

    if user["nedelya"] == "Чётная неделя":
        ikb.row(InlineKeyboardButton("🔄 Чётная неделя", callback_data="change_week"))
        user['nedelya'] = "Нечётная неделя"
    else:
        ikb.row(InlineKeyboardButton("🔄 Нечётная неделя", callback_data="change_week"))
        user['nedelya'] = "Чётная неделя"

    ikb.row(InlineKeyboardButton("Поменять группу", callback_data="start"))

    msg = await create_oneday_timetable(user["kurs"], user['group'], user["nedelya"], user["day"])

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=user_base[str(message.from_user.id)]["last_message"],
                                text=f"{msg}",
                                reply_markup=ikb)

@dp.callback_query_handler(text="start")
async def start_clb(message: types.CallbackQuery):
    # инлайн клавиатура
    ikb = InlineKeyboardMarkup()
    for i in all_groups:
        ikb.row(InlineKeyboardButton(i + " курс", callback_data=i + "kurs"))
        kurs_handlers.append(i + "kurs")

    # отправляем приветственное сообщение
    msg = await bot.edit_message_text(text="Привет! Я помогу тебе найти твоё расписание! На каком курсе ты учишься?",
                                      reply_markup=ikb,
                                      chat_id=message.from_user.id,
                                      message_id=user_base[str(message.from_user.id)]["last_message"])

    # получаем реальное время
    await get_time()

    # добавляем действие клиента в базу, сохраняем id последнего сообщения
    user_base[str(message.from_user.id)]["cjm"].append(f"{time} = <b>Смена группы</b>")








#ЗАГРУЗКА СИСТЕМ ФАЙЛА
@dp.message_handler(content_types=ContentType.DOCUMENT)
async def base_in(doc: types.Message):
    await doc.delete()
    file = await doc.document.download(destination_file="system_file.txt")

    stroka = open("system_file.txt", "r").readline().replace("'", chr(34))
    dictionary = json.loads(stroka)

    await add_base(dictionary)

    await get_time()

    await user_file()
    media = types.MediaGroup()
    media.attach_document(types.InputFile('system_file.txt'))
    media.attach_document(types.InputFile('cjm_file.txt'))
    media.attach_document(types.InputFile('id_file.txt'))
    media.attach_document(types.InputFile('username_file.txt'), caption=f"База загружена\n{time}")
    await statistic_bot.send_media_group(chat_id=doc.from_user.id,
                                         media=media)

#ПРОЧИЕ КОМАНДЫ
@dp.message_handler()
async def error(message: types.Message):
    await message.delete()
    if str(message.from_user.id) in admin:
        if message.text in user_base:
            info = await client_info(message.text)

            await user_file()
            media = types.MediaGroup()
            media.attach_document(types.InputFile('system_file.txt'))
            media.attach_document(types.InputFile('cjm_file.txt'))
            media.attach_document(types.InputFile('id_file.txt'))
            media.attach_document(types.InputFile('username_file.txt'), caption=f'{info}')

            await statistic_bot.send_media_group(chat_id=message.from_user.id,
                                                 media=media)
        if message.text=="clear":
            for i in user_base:
                await bot.delete_message(chat_id=str(i),
                                         message_id=user_base[str(message.from_user.id)]['last_message'])

        if message.text=="create":
            await create_raspisanie()

    else:
        for i in admin:
            await statistic_bot.send_message(chat_id=i,
                                             text=f"@{message.from_user.username}\n"
                                                  f"<code>{message.from_user.id}</code>\n\n"
                                                  f"<b>ошибка:</b> {message.text}")

if __name__ == "__main__":
    executor.start_polling(dp,
                           skip_updates=True)


