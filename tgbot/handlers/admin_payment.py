# - *- coding: utf- 8 - *-
import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from pycrystalpay import CrystalPay

from tgbot.keyboards.inline_admin import payment_choice_finl
from tgbot.loader import dp
from tgbot.services.api_crystal import CrystalAPI
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_sqlite import update_paymentx, get_paymentx, update_crystal, get_crystal, update_wm
from tgbot.services.api_wm import wmAPI
from tgbot.utils.misc.bot_filters import IsAdmin


###################################################################################
############################# ВЫБОР СПОСОБА ПОПОЛНЕНИЯ ############################
# Открытие способов пополнения
@dp.message_handler(IsAdmin(), text="🖲 Способы пополнения", state="*")
async def payment_systems(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🖲 Выберите способ пополнения</b>", reply_markup=payment_choice_finl())


# Включение/выключение самих способов пополнения
@dp.callback_query_handler(IsAdmin(), text_startswith="change_payment:")
async def payment_systems_edit(call: CallbackQuery):
    way_pay = call.data.split(":")[1]
    way_status = call.data.split(":")[2]

    if way_pay == 'Crystal':
        crystal_info = get_crystal()
        try:
            crystal = CrystalPay(crystal_info['login'], crystal_info['secret'])
            if way_status == 'False':
                update_crystal(status=0)
            else:
                update_crystal(status=1)
        except:
            await call.answer("❗ Добавьте Crystal перед включением Способов пополнений.", True)
    elif way_pay == 'WebMoney':
        try:
            if way_status == 'False':
                update_wm(status=0)
            else:
                update_wm(status=1)
        except:
            await call.answer("❗ Добавьте WebMoney перед включением Способов пополнений.", True)
    else:

        get_payment = get_paymentx()

        if get_payment['qiwi_login'] != "None" and get_payment['qiwi_token'] != "None" or way_status == "False":
            if way_pay == "Form":
                if get_payment['qiwi_secret'] != "None" or way_status == "False":
                    update_paymentx(way_form=way_status)
                else:
                    await call.answer(
                        "❗ Приватный ключ отсутствует. Измените киви и добавьте приватный ключ для включения оплаты по Форме",
                        True)
            elif way_pay == "Number":
                update_paymentx(way_number=way_status)
            elif way_pay == "Nickname":
                status, response = await (await QiwiAPI(call)).get_nickname()
                if status:
                    update_paymentx(way_nickname=way_status, qiwi_nickname=response)
                else:
                    await call.answer(response, True)
        else:
            await call.answer("❗ Добавьте киви кошелёк перед включением Способов пополнений.", True)

    try:
        await call.message.edit_text("<b>🖲 Выберите способ пополнения</b>", reply_markup=payment_choice_finl())
    except:
        pass


###################################################################################
####################################### QIWI ######################################
# Изменение QIWI кошелька
@dp.message_handler(IsAdmin(), text="🥝 Изменить QIWI", state="*")
async def payment_qiwi_edit(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_qiwi_login")
    await message.answer("<b>🥝 Введите <code>номер (через +7, +380)</code> QIWI кошелька</b>")


# Проверка работоспособности QIWI
@dp.message_handler(IsAdmin(), text="🥝 Проверить QIWI", state="*")
async def payment_qiwi_check(message: Message, state: FSMContext):
    await state.finish()

    await (await QiwiAPI(message, check_pass=True)).pre_checker()


# Баланс QIWI
@dp.message_handler(IsAdmin(), text="🥝 Баланс QIWI", state="*")
async def payment_qiwi_balance(message: Message, state: FSMContext):
    await state.finish()

    await (await QiwiAPI(message)).get_balance()


######################################## ПРИНЯТИЕ QIWI ########################################
# Принятие логина для QIWI
@dp.message_handler(IsAdmin(), state="here_qiwi_login")
async def payment_qiwi_edit_login(message: Message, state: FSMContext):
    if message.text.startswith("+"):
        await state.update_data(here_qiwi_login=message.text)

        await state.set_state("here_qiwi_token")
        await message.answer(
            "<b>🥝 Введите <code>токен API</code> QIWI кошелька</b>\n"
            "❕ Получить можно тут 👉 <a href='https://qiwi.com/api'><b>Нажми на меня</b></a>\n"
            "❕ При получении токена, ставьте только первые 3 галочки.",
            disable_web_page_preview=True
        )
    else:
        await message.answer("<b>❌ Номер должен начинаться с + <code>(+7..., +380...)</code></b>\n"
                             "🥝 Введите <code>номер (через +7, +380)</code> QIWI кошелька")


# Принятие токена для QIWI
@dp.message_handler(IsAdmin(), state="here_qiwi_token")
async def payment_qiwi_edit_token(message: Message, state: FSMContext):
    await state.update_data(here_qiwi_token=message.text)

    await state.set_state("here_qiwi_secret")
    await message.answer(
        "<b>🥝 Введите <code>Секретный ключ</code></b>\n"
        "❕ Получить можно тут 👉 <a href='https://qiwi.com/p2p-admin/transfers/api'><b>Нажми на меня</b></a>\n"
        "❕ Вы можете пропустить добавление оплаты по Форме, отправив: <code>0</code>",
        disable_web_page_preview=True
    )


# Принятие приватного ключа для QIWI
@dp.message_handler(IsAdmin(), state="here_qiwi_secret")
async def payment_qiwi_edit_secret(message: Message, state: FSMContext):
    async with state.proxy() as data:
        qiwi_login = data['here_qiwi_login']
        qiwi_token = data['here_qiwi_token']
        if message.text == "0": qiwi_secret = "None"
        if message.text != "0": qiwi_secret = message.text

    await state.finish()

    cache_message = await message.answer("<b>🔄 Проверка введённых QIWI данных...</b>")
    await asyncio.sleep(0.5)

    await (await QiwiAPI(cache_message, qiwi_login, qiwi_token, qiwi_secret, True)).pre_checker()


###################################################################################
####################################### CRYSTAL ###################################
# Изменение CRYSTAL кошелька
@dp.message_handler(IsAdmin(), text="💎 Изменить Crystal", state="*")
async def payment_crystal_edit(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_crystal_login")
    await message.answer("<b>💎 Введите <code>логин</code> Crystal</b>")


# Проверка работоспособности CRYSTAL
@dp.message_handler(IsAdmin(), text="💎 Проверить Crystal", state="*")
async def payment_crystal_check(message: Message, state: FSMContext):
    await state.finish()

    await (await CrystalAPI(message, check_pass=True)).pre_checker()


# Баланс CRYSTAL
@dp.message_handler(IsAdmin(), text="💎 Баланс Crystal", state="*")
async def payment_crystal_balance(message: Message, state: FSMContext):
    await state.finish()

    await (await CrystalAPI(message)).get_balance()


# Принятие логина для QIWI
@dp.message_handler(IsAdmin(), state="here_crystal_login")
async def payment_crystal_edit_login(message: Message, state: FSMContext):
    await state.update_data(here_crystal_login=message.text)

    await state.set_state("here_crystal_secret")
    await message.answer(
        "<b>💎 Введите <code>Секретный ключ</code></b>\n"
    )


@dp.message_handler(IsAdmin(), state="here_crystal_secret")
async def payment_crystal_edit_secret(message: Message, state: FSMContext):
    async with state.proxy() as data:
        crystal_login = data['here_crystal_login']
        if message.text == "0": crystal_secret = "None"
        if message.text != "0": crystal_secret = message.text

    await state.finish()

    cache_message = await message.answer("<b>🔄 Проверка введённых Crystal данных...</b>")
    await asyncio.sleep(0.5)

    await (await CrystalAPI(message, login=crystal_login, secret=crystal_secret, add_pass=True)).pre_checker()


###################################################################################
####################################### WebMoney ##################################
# Изменение WebMoney кошелька
@dp.message_handler(IsAdmin(), text="🌍 Изменить WebMoney", state="*")
async def payment_crystal_edit(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_wm_wallet")
    await message.answer("<b>🌍 Введите <code>wallet</code> WebMoney</b>")


# Проверка работоспособности WebMoney
@dp.message_handler(IsAdmin(), text="🌍 Проверить WebMoney", state="*")
async def payment_crystal_check(message: Message, state: FSMContext):
    await state.finish()

    await (await wmAPI(message, check_pass=True)).pre_checker()


# Баланс WebMoney
@dp.message_handler(IsAdmin(), text="🌍 Баланс WebMoney", state="*")
async def payment_crystal_balance(message: Message, state: FSMContext):
    await state.finish()

    await (await wmAPI(message)).get_balance()


@dp.message_handler(IsAdmin(), state="here_wm_wallet")
async def payment_wm_edit_wallet(message: Message, state: FSMContext):
    await state.update_data(here_wm_wallet=message.text)

    await state.set_state("here_wm_type")
    await message.answer(
        "<b>🌍 Укажите тип Wallet (WMK, WMZ...)</b>\n"
    )




@dp.message_handler(IsAdmin(), state="here_wm_type")
async def payment_wm_edit_key(message: Message, state: FSMContext):
    async with state.proxy() as data:
        wm_wallet = data['here_wm_wallet']
        wm_type = message.text


    await state.finish()

    cache_message = await message.answer("<b>🔄 Проверка введённых данных...</b>")
    await asyncio.sleep(0.5)

    await (await wmAPI(cache_message, wallet=wm_wallet, type=wm_type, add_pass=True)).pre_checker()
