# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.data.config import bot_version, PATH_LOGS, DATABASE_PATH
from tgbot.keyboards.reply_z_all import payments_frep, settings_frep, functions_frep, items_frep
from tgbot.loader import dp
from tgbot.utils.const_functions import get_date
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.utils.misc_functions import get_statisctics


# Платежные системы
@dp.message_handler(IsAdmin(), text="🔑 Платежные системы", state="*")
async def admin_payment(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🔑 Настройка платежных системы.</b>", reply_markup=payments_frep())


# Настройки бота
@dp.message_handler(IsAdmin(), text="⚙ Настройки", state="*")
async def admin_settings(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⚙ Основные настройки бота.</b>", reply_markup=settings_frep())


# Общие функции
@dp.message_handler(IsAdmin(), text="🔆 Общие функции", state="*")
async def admin_functions(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🔆 Выберите нужную функцию.</b>", reply_markup=functions_frep(message.from_user.id))


# Управление товарами
@dp.message_handler(IsAdmin(), text="🎁 Управление товарами", state="*")
async def admin_products(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🎁 Редактирование товаров.</b>", reply_markup=items_frep())


# Cтатистики бота
@dp.message_handler(IsAdmin(), text="📜 Статистика", state="*")
async def admin_statistics(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(get_statisctics())


# Получение БД
@dp.message_handler(IsAdmin(), commands=['db', 'database'], state="*")
async def admin_database(message: Message, state: FSMContext):
    await state.finish()

    with open(DATABASE_PATH, "rb") as document:
        await message.answer_document(document,
                                      caption=f"<b>📦 BACKUP</b>\n"
                                              f"<code>🕰 {get_date()}</code>")


# Получение Логов
@dp.message_handler(IsAdmin(), commands=['log', 'logs'], state="*")
async def admin_log(message: Message, state: FSMContext):
    await state.finish()

    with open(PATH_LOGS, "rb") as document:
        await message.answer_document(document,
                                      caption=f"<b>🖨 LOGS</b>\n"
                                              f"<code>🕰 {get_date()}</code>")


# Получение версии бота
@dp.message_handler(commands="version", state="*")
async def admin_version(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(f"<b>❇ Текущая версия бота: <code>{bot_version}</code></b>")
