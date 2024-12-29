from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import aiosqlite
import asyncio
import logging
import sys
from datetime import datetime, timedelta
import tracemalloc

tracemalloc.start()

TOKEN = ''
ADMIN = 

text = """
Меня зовут Андрей (или вы можете обращаться ко мне как @exfador).
Этот бот создан для быстрого управления и оперативного ответа на ваши вопросы.
Выберите то, что вам нужно, и получите результат в сжатые сроки.
"""

info_user = f"""
Мне <b>18 лет</b>, и я являюсь <b>Python-разработчиком</b>.  
Мои нынешние навыки включают:  
• Создание <b>Telegram-ботов</b> и <b>Discord-ботов</b>  
• Разработку <b>скриптов</b> и <b>софтов</b>  

Мои знания библиотек:  
• <b>telebot</b>, <b>aiogram</b>, <b>pyrogram</b>, <b>discord.py</b>, <b>telethon</b>  
• <b>sqlite3</b>, <b>requests</b>, <b>beautifulsoup4</b>, <b>pyyaml</b>  
• <b>asyncio</b>, <b>aiohttp</b>, <b>aiosqlite</b>, <b>aiomysql</b>  
• <b>selenium</b>, <b>playwright</b>, <b>qt5</b>  
"""

working_conditions = """
Работа осуществляется по предоплате 50/100 % | Использование гаранта LZT.​
Все права на созданный код принадлежат нашей компании/разработчику, если не оговорено иное при заказе.​
Мы оставляем за собой право отказать в обслуживании клиента в случае проявления неадекватного или неприемлемого поведения со стороны заказчика.​
При отказе от заказа со стороны заказчика после начала работ или по причинам, не связанным с нашими ошибками или невыполнением обязательств, предоплата не
возвращается.​
"""

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

buttons = [
    [
        InlineKeyboardButton(text='Портфолио', url='https://t.me/medfaqes'),
        InlineKeyboardButton(text='Профиль', url='https://t.me/exfador'),
    ],
    [
        InlineKeyboardButton(text='Информация обо мне', callback_data='info'),
    ],
    [
        InlineKeyboardButton(text='Условия работы', callback_data='uslovia'),
    ],
    [
        InlineKeyboardButton(text='Отзывы', url='https://t.me/exfador_reviews'),
    ],
    [
        InlineKeyboardButton(text='Спамблок', callback_data='sp'),
    ]
]

menu = InlineKeyboardMarkup(inline_keyboard=buttons)



buttons_back = [
    [
        InlineKeyboardButton(text='Назад', callback_data='back'),
    ]
]

menu_back = InlineKeyboardMarkup(inline_keyboard=buttons_back)

user_messages = {}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    username = message.from_user.username
    user_id = message.from_user.id
    await register_account(username, user_id)
    hello = FSInputFile('image/hello.webp')
    sent_document = await bot.send_document(chat_id=user_id, document=hello)
    sent_message = await message.answer(f"Привет <b> {message.from_user.full_name} </b>\n{text}", reply_markup=menu, parse_mode='HTML')

    user_messages[user_id] = [sent_document.message_id, sent_message.message_id]




@dp.callback_query(F.data == 'back')
async def info_handler(callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id

    await delete_user_messages(user_id)

    hello = FSInputFile('image/info.webp')
    sent_document = await bot.send_document(chat_id=user_id, document=hello)
    sent_message = await bot.send_message(user_id, f"Уходил ты ненадолго конечно!", reply_markup=menu)

    user_messages[user_id] = [sent_document.message_id, sent_message.message_id]



@dp.callback_query(F.data == 'sp')
async def spam_block(callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    if username is None:
        await callback_query.answer("Ты не можешь запросить спамблок, т.к твой username не указан.", show_alert=True)
    else:
        result = await spam_time_and_check(user_id) 
        if isinstance(result, str):
            await callback_query.answer(result, show_alert=True)
        else:
            await callback_query.answer("Оповестил администратора о том, что у Вас спамблок. Ожидайте", show_alert=True)
            await bot.send_message(chat_id=ADMIN, text=f"""
    Пользователь: @{callback_query.from_user.username} попросил связаться с ним.
    """)


@dp.callback_query(F.data == 'info')
async def info_handler(callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id

    await delete_user_messages(user_id)

    hello = FSInputFile('image/info.webp')
    sent_document = await bot.send_document(chat_id=user_id, document=hello)
    sent_message = await bot.send_message(user_id, f"{info_user}", reply_markup=menu_back, parse_mode='HTML')

    user_messages[user_id] = [sent_document.message_id, sent_message.message_id]


@dp.callback_query(F.data == 'uslovia')
async def uslovia_handler(callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id


    await delete_user_messages(user_id)

    hello = FSInputFile('image/work.webp')
    sent_document = await bot.send_document(chat_id=user_id, document=hello)
    sent_message = await bot.send_message(user_id, f"{working_conditions}", reply_markup=menu_back)

    user_messages[user_id] = [sent_document.message_id, sent_message.message_id]


async def delete_user_messages(user_id):
    if user_id in user_messages:
        for message_id in user_messages[user_id]:
            try:
                await bot.delete_message(chat_id=user_id, message_id=message_id)
            except Exception as e:
                logging.error(f"Failed to delete message {message_id}: {e}")
        del user_messages[user_id]


async def main() -> None:
    try:
        async with aiosqlite.connect('users.db') as db:
            cursor = await db.cursor()
            await cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                report_time INTEGER NOT NULL
            )''')
            await db.commit()
            await dp.start_polling(bot)

    except Exception as ee:
        print(f"Cannot connect to the database: {ee}")


async def register_account(username, user_id) -> None:
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.cursor()
        await cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        result = await cursor.fetchone()
        if not result:
            current_time = int(datetime.utcnow().timestamp())
            if username is None:
                username = 'NoUsername' 
            await cursor.execute('INSERT INTO users (id, username, report_time) VALUES (?, ?, ?)',
                                 (user_id, username, 0))
            await db.commit()
            await bot.send_message(chat_id=ADMIN, text=f"""
Новый пользователь в боте: @{username}.
""")
            

async def spam_time_and_check(user_id) -> None:
    async with aiosqlite.connect('users.db') as db:
        time_limit = 300
        cursor = await db.cursor()
        await cursor.execute('SELECT report_time FROM users WHERE id = ?', (user_id,))
        result = await cursor.fetchone()

        if result:
            last_report_time = result[0]
            last_report_time_dt = datetime.fromtimestamp(last_report_time)
            current_time = datetime.utcnow()

            if (current_time - last_report_time_dt).total_seconds() >= time_limit:
                new_report_time = current_time + timedelta(seconds=time_limit)
                await cursor.execute('UPDATE users SET report_time = ? WHERE id = ?',
                                     (int(new_report_time.timestamp()), user_id))
                await db.commit()
                return None
            else:
                remaining_time = time_limit - (current_time - last_report_time_dt).total_seconds()
                minutes_left = int(remaining_time // 60)
                seconds_left = int(remaining_time % 60)
                return f'Вы не можете сейчас отправить оповещение администратору, Вам будет доступно через: {minutes_left} минут(ы) и {seconds_left} секунд(ы)'
        else:
            return 'Ошибка, аккаунт не найден в базе данных.'


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())