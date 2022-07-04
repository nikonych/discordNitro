# - *- coding: utf- 8 - *-
import requests

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile

from tgbot.keyboards.inline_user import user_support_finl
from tgbot.keyboards.reply_z_all import menu_frep
from tgbot.loader import dp
from tgbot.services.api_sqlite import get_settingsx, get_userx
from tgbot.utils.misc.bot_filters import IsBuy, IsRefill, IsWork, IsBan

# Игнор-колбэки покупок
prohibit_buy = ['buy_category_open', 'buy_category_return', 'buy_category_nextp', 'buy_category_backp',
                'buy_position_open', 'buy_position_return', 'buy_position_nextp', 'buy_position_backp',
                'buy_purchase_select', 'here_purchase_count', 'xpurchase_item']

# Игнор-колбэки пополнений
prohibit_refill = ['user_refill', 'refill_choice', 'Pay:', 'Pay:Form', 'Pay:Number', 'Pay:Nickname']


####################################################################################################
######################################## ТЕХНИЧЕСКИЕ РАБОТЫ ########################################
# Фильтр на технические работы - сообщение
@dp.message_handler(IsWork(), IsBan(), state="*")
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
@dp.callback_query_handler(IsWork(), IsBan(), state="*")
async def filter_work_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Бот находится на технических работах.", True)


####################################################################################################
########################################### СТАТУС ПОКУПОК #########################################
# Фильтр на доступность покупок - сообщение
@dp.message_handler(IsBuy(), IsBan(), text="🎁 Купить", state="*")
@dp.message_handler(IsBuy(), state="here_purchase_count")
async def filter_buy_message(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⛔ Покупки временно отключены.</b>")


# Фильтр на доступность покупок - колбэк
@dp.callback_query_handler(IsBan(), IsBuy(), text_startswith=prohibit_buy, state="*")
async def filter_buy_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Покупки временно отключены.", True)


####################################################################################################
######################################### СТАТУС ПОПОЛНЕНИЙ ########################################
# Фильтр на доступность пополнения - сообщение
@dp.message_handler(IsBan(), IsRefill(), state="here_pay_amount")
async def filter_refill(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⛔ Пополнение временно отключено.</b>")


# Фильтр на доступность пополнения - колбэк
@dp.callback_query_handler(IsBan(), IsRefill(), text_startswith=prohibit_refill, state="*")
async def filter_refill(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Пополнение временно отключено.", True)


####################################################################################################
############################################## ПРОЧЕЕ ##############################################
# Открытие главного меню
@dp.message_handler(text=['⬅ Главное меню', '/start'], state="*")
async def main_start(message: Message, state: FSMContext):
    await state.finish()
    # print(open('tgbot/data/resourses/photo/main.jpg', 'rb').name)
    await message.answer_photo(open('tgbot/data/resourses/photo/main.jpg', 'rb'), caption=f"<b>👋 Приветик {message.from_user.first_name}!</b>\n"
                         "❤️ Добро пожаловать в самый лучший магазин, по продаже Discord Nitro!!!\n"
                         " ",
                         reply_markup=menu_frep(message.from_user.id))
