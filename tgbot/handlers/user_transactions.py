# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from pycrystalpay import CrystalPay

from tgbot.data import config
from tgbot.keyboards.inline_user import refill_bill_finl, refill_choice_finl
from tgbot.loader import dp, bot
from tgbot.services.api_crystal import CrystalAPI
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_sqlite import update_userx, get_refillx, add_refillx, get_userx, get_crystal, has_referer, \
    get_all_users_id, get_balance
from tgbot.utils.const_functions import get_date, get_unix
from tgbot.utils.misc_functions import send_admins

min_input_qiwi = 5  # Минимальная сумма пополнения в рублях


# Выбор способа пополнения
@dp.callback_query_handler(text="user_refill", state="*")
async def refill_way(call: CallbackQuery, state: FSMContext):
    get_kb = refill_choice_finl()

    if get_kb is not None:
        await call.message.edit_text("<b>💰 Выберите способ пополнения</b>",
                                     reply_markup=get_kb)
    else:
        await call.answer("⛔ Пополнение временно недоступно", True)


# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="refill_choice", state="*")
async def refill_way_choice(call: CallbackQuery, state: FSMContext):
    get_way = call.data.split(":")[1]

    await state.update_data(here_pay_way=get_way)

    await state.set_state("here_pay_amount")
    await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")


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
            await state.finish()
            if get_way == 'Crystal':
                get_payment, get_message = await (
                    await CrystalAPI(cache_message)
                ).bill_pay(pay_amount)
            else:
                get_message, get_link, receipt = await (
                    await QiwiAPI(cache_message, user_bill_pass=True)
                ).bill_pay(pay_amount, get_way)

            if get_message:
                if get_way == 'Crystal':
                    print(get_payment.id)
                    await cache_message.edit_text(get_message, reply_markup=refill_bill_finl(get_payment.url, get_payment.id, get_way))
                else:
                    await cache_message.edit_text(get_message, reply_markup=refill_bill_finl(get_link, receipt, get_way))
        else:
            await cache_message.edit_text(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")


###################################################################################
################################ ПРОВЕРКА ПЛАТЕЖЕЙ ################################
# Проверка оплаты через форму
@dp.callback_query_handler(text_startswith="Pay:Form")
async def refill_check_form(call: CallbackQuery):
    receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        await QiwiAPI(call, user_check_pass=True)
    ).check_form(receipt)

    if pay_status == "PAID":
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, "Form")
        else:
            await call.answer("❗ Ваше пополнение уже было зачислено.", True)
    elif pay_status == "EXPIRED":
        await call.message.edit_text("<b>❌ Время оплаты вышло. Платёж был удалён.</b>")
    elif pay_status == "WAITING":
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)
    elif pay_status == "REJECTED":
        await call.message.edit_text("<b>❌ Счёт был отклонён.</b>")


# Проверка оплаты по переводу (по нику или номеру)
@dp.callback_query_handler(text_startswith=['Pay:Number', 'Pay:Nickname'])
async def refill_check_send(call: CallbackQuery):
    way_pay = call.data.split(":")[1]
    receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        await QiwiAPI(call, user_check_pass=True)
    ).check_send(receipt)

    if pay_status == 1:
        await call.answer("❗ Оплата была произведена не в рублях.", True, cache_time=5)
    elif pay_status == 2:
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)
    elif pay_status == 4:
        pass
    else:
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, way_pay)
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)


@dp.callback_query_handler(text_startswith="Pay:Crystal")
async def refill_check_form(call: CallbackQuery):
    receipt = call.data.split(":")[2]

    crystal_info = get_crystal()
    crystal = CrystalPay(crystal_info['login'], crystal_info['secret'])
    payment = crystal.construct_payment_by_id(receipt)

    print(payment.url)
    isPaid = payment.if_paid()
    isPaid = True

    if isPaid:
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, payment.amount, "Crystal")
        else:
            await call.answer("❗ Ваше пополнение уже было зачислено.", True)
    else:
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)



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

    await call.message.edit_text(f"<b>💰 Вы пополнили баланс на сумму <code>{amount}₽</code>\n"
                                 f"🧾 Чек: <code>#{receipt}</code></b>")

    await send_admins(
        f"👤 Пользователь: @{get_user['user_login']} | <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> | <code>{get_user['user_id']}</code>\n"
        f"💰 Сумма пополнения: <code>{amount}₽</code>\n"
        f"🧾 Чек: <code>#{receipt}</code>"
    )

    if int(has_referer(user_id=call.from_user.id)) != 0 and int(
            has_referer(user_id=call.from_user.id)) in get_all_users_id():
        balance = get_balance(has_referer(user_id=call.from_user.id))
        balance += int(int(amount) * int(config.PERCENT) * 0.01)
        update_userx(user_id=int(has_referer(user_id=call.from_user.id)), user_balance=balance)
        await bot.send_message(int(has_referer(user_id=call.from_user.id)),
                               f"От вашего реферала вам поступило: <code>{int(int(amount) * int(config.PERCENT) * 0.01)}₽</code>!")
