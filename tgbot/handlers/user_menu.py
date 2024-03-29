# - *- coding: utf- 8 - *-
import asyncio
import datetime
from typing import Union

import requests
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from dateutil import relativedelta

from tgbot.data import config
from tgbot.data.config import bot_description
from tgbot.keyboards.inline_user import user_support_finl, products_open_finl, products_confirm_finl, refill_choice_finl
from tgbot.keyboards.inline_z_all import profile_open_inl, close_inl, close_referer, buy_vip_inl
from tgbot.keyboards.inline_z_page import *
from tgbot.keyboards.reply_z_all import menu_frep
from tgbot.loader import dp, bot
from tgbot.services.api_sqlite import *
from tgbot.utils.const_functions import get_date, split_messages, get_unix
from tgbot.utils.misc.bot_filters import IsBan
from tgbot.utils.misc_functions import open_profile_my, upload_text, get_faq


# Открытие товаров
@dp.message_handler(IsBan(),text="🎁 Купить", state="*")
async def user_shop(message: Message, state: FSMContext):
    await state.finish()

    if len(get_all_categoriesx()) >= 1:
        await message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption="<b>🎁 Выберите нужный вам товар:</b>",
                                   reply_markup=products_item_category_open_fp(0))
    else:
        await message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption="<b>🎁 Товары в данное время отсутствуют.</b>")


# Открытие профиля
@dp.message_handler(IsBan(), text="👮‍♀️ Профиль", state="*")
async def user_profile(message: Message, state: FSMContext):
    await state.finish()
    me = await bot.get_me()
    await message.answer_photo(open('tgbot/data/resourses/photo/profile.jpg', 'rb'), caption=open_profile_my(message.from_user.id, me), reply_markup=profile_open_inl)


# Открытие FAQ
@dp.message_handler(IsBan(), text=["📕 Правила", "/faq"], state="*")
async def user_faq(message: Message, state: FSMContext):
    await state.finish()

    send_message = get_settingsx()['misc_faq']
    if send_message == "None":
        send_message = f"ℹ Информация. Измените её в настройках бота.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n{bot_description}"

    await message.answer_photo(open('tgbot/data/resourses/photo/rule.jpg', 'rb'),
                               caption=get_faq(message.from_user.id, send_message), reply_markup=close_inl)


# Открытие сообщения с ссылкой на поддержку
@dp.message_handler(IsBan(), text=["☎ Поддержка", "/support"], state="*")
async def user_support(message: Message, state: FSMContext):
    await state.finish()

    user_support = get_settingsx()['misc_support']
    if str(user_support).isdigit():
        get_user = get_userx(user_id=user_support)

        if len(get_user['user_login']) >= 1:
            await message.answer_photo(open('tgbot/data/resourses/photo/help.jpg', 'rb'),
                                       caption="<b>☎ Нажмите кнопку ниже для связи с Администратором.</b>",
                                       reply_markup=user_support_finl(get_user['user_login']))
            return
        else:
            update_settingsx(misc_support="None")

    await message.answer(f"☎ Контакты. Измените их в настройках бота.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n{bot_description}",
                         disable_web_page_preview=True)


################################################################################################
# Просмотр истории покупок
@dp.callback_query_handler(text="user_history", state="*")
async def user_history(call: CallbackQuery, state: FSMContext):
    last_purchases = last_purchasesx(call.from_user.id, 5)

    if len(last_purchases) >= 1:
        await call.answer("🎁 Последние 5 покупок")
        await call.message.delete()

        for purchases in last_purchases:
            link_items = await upload_text(call, purchases['purchase_item'])

            await call.message.answer(f"<b>🧾 Чек: <code>#{purchases['purchase_receipt']}</code></b>\n"
                                      f"🎁 Товар: <code>{purchases['purchase_position_name']} | {purchases['purchase_count']}шт | {purchases['purchase_price']}₽</code>\n"
                                      f"🕰 Дата покупки: <code>{purchases['purchase_date']}</code>\n"
                                      f"🔗 Товары: <a href='{link_items}'>кликабельно</a>")

        await call.message.answer(open_profile_my(call.from_user.id), reply_markup=profile_open_inl)
    else:
        await call.answer("❗ У вас отсутствуют покупки", True)


@dp.callback_query_handler(text="buy_vip", state="*")
async def user_buy_vip(call: CallbackQuery, state: FSMContext):
    await state.finish()

    send_message = get_settingsx()['misc_vip']
    if send_message == "None" or send_message == None or send_message == 'vip':
        send_message = f"ℹ Информация. Измените её в настройках бота.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n{bot_description}"

    await call.message.edit_caption(
                               caption=send_message, reply_markup=buy_vip_inl)


@dp.callback_query_handler(text="buy_vip_money", state="*")
async def user_buy_vip(call: CallbackQuery, state: FSMContext):
    await state.finish()

    user = get_userx(user_id=call.from_user.id)
    balance = user['user_balance']
    nextmonth = datetime.date.today() + relativedelta.relativedelta(months=1)
    if user['user_role'] != 'VIP' and user['user_role'] != 'Admin':
        if balance >= 750:
            update_userx(user_id=call.from_user.id, user_balance=balance-750, user_role='VIP', vip_date=nextmonth)
            await call.answer("🎁 Покупка прошла успешно!")
            me = await bot.get_me()
            await call.message.edit_caption(caption=open_profile_my(call.from_user.id, me), reply_markup=profile_open_inl)
        else:
            await call.answer("❗ У вас недостаточно средств!")
            get_kb = refill_choice_finl()

            if get_kb is not None:
                await call.message.edit_caption("<b>💰 Выберите способ пополнения</b>",
                                                reply_markup=get_kb)
            else:
                await call.answer("⛔ Пополнение временно недоступно", True)
    elif user['user_role'] == 'Admin':
        await call.answer("❗ Зачем? Вы же Админ!")
    else:
        await call.answer("❗ У вас уже есть VIP!")


# Возвращение к профилю
@dp.callback_query_handler(text="user_profile", state="*")
async def user_profile_return(message: Union['Message', 'CallbackQuery'], state: FSMContext):
    me = await bot.get_me()
    await message.message.edit_caption(open_profile_my(message.from_user.id, me), reply_markup=profile_open_inl)


# Referer system
@dp.message_handler(IsBan(), text="🤑 Реферальная система")
async def user_referer(message: Message, state: FSMContext):
    percent = config.PERCENT
    me = await bot.get_me()
    user_id = message.from_user.id
    link = 'https://t.me/' + me.username + '?start=' + str(user_id)
    await message.answer_photo(open('tgbot/data/resourses/photo/referer.jpg', 'rb'),
                               caption=
                               f'🤍 Реферальная система 🤍\n'
                               '\n'
                               '🔗<i> Ссылка: </i>\n'
                               f'<code>{link}</code>\n'
                               f'\n'
                               f'<i>📔 Наша реферальная система позволит вам заработать крупную сумму без вложений.'
                               f' Вам необходимо лишь давать свою ссылку друзьям и вы будете получать пожизненно {percent}% с их пополнений в боте</i>',
                               reply_markup=close_inl
                               )


################################################################################################
######################################### ПОКУПКА ТОВАРА #######################################
########################################### КАТЕГОРИИ ##########################################
# Открытие категорий для покупки
@dp.callback_query_handler(text_startswith="buy_category_open", state="*")
async def user_purchase_category_open(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])

    get_category = get_categoryx(category_id=category_id)
    get_positions = get_positionsx(category_id=category_id)


    if len(get_positions) >= 1:
        await call.message.edit_caption("<b>🎁 Выберите нужный вам товар:</b>",
                                     reply_markup=products_item_position_open_fp(0, category_id, call.from_user.id))
    else:
        await call.answer(f"❕ Товары в категории {get_category['category_name']} отсутствуют")


# Вернуться к категориям для покупки
@dp.callback_query_handler(text_startswith="buy_category_return", state="*")
async def user_purchase_category_return(call: CallbackQuery, state: FSMContext):
    get_categories = get_all_categoriesx()

    if len(get_categories) >= 1:
        await call.message.edit_caption("<b>🎁 Выберите нужный вам товар:</b>",
                                     reply_markup=products_item_category_open_fp(0))
    else:
        await call.message.edit_caption("<b>🎁 Товары в данное время отсутствуют.</b>")
        await call.answer("❗ Категории были изменены или удалены")


# Следующая страница категорий для покупки
@dp.callback_query_handler(text_startswith="buy_category_nextp", state="*")
async def user_purchase_category_next_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_caption("<b>🎁 Выберите нужный вам товар:</b>",
                                 reply_markup=products_item_category_next_page_fp(remover))


# Предыдущая страница категорий для покупки
@dp.callback_query_handler(text_startswith="buy_category_backp", state="*")
async def user_purchase_category_prev_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_caption("<b>🎁 Выберите нужный вам товар:</b>",
                                 reply_markup=products_item_category_back_page_fp(remover))


########################################### ПОЗИЦИИ ##########################################
# Открытие позиции для покупки
@dp.callback_query_handler(text_startswith="buy_position_open", state="*")
async def user_purchase_position_open(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])
    category_id = int(call.data.split(":")[3])

    get_user = get_userx(user_id=call.from_user.id)
    get_position = get_positionx(position_id=position_id)
    get_category = get_categoryx(category_id=category_id)
    get_items = get_itemsx(position_id=position_id)
    if get_user['user_role'] == "VIP":
        get_position['position_price'] = get_position['position_price'] / 2

    if get_position['position_description'] == "0":
        text_description = ""
    else:
        text_description = f"\n📜 Описание:\n" \
                           f"{get_position['position_description']}"

    send_msg = f"<b>🎁 Покупка товара:</b>\n" \
               f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
               f"🏷 Название: <code>{get_position['position_name']}</code>\n" \
               f"🗃 Категория: <code>{get_category['category_name']}</code>\n" \
               f"💰 Стоимость: <code>{get_position['position_price']}₽</code>\n" \
               f"📦 Количество: <code>{len(get_items)}шт</code>" \
               f"{text_description}"

    if len(get_position['position_photo']) >= 5:
        await call.message.delete()
        await call.message.answer_photo(get_position['position_photo'],
                                        send_msg, reply_markup=products_open_finl(position_id, remover, category_id))
    else:
        await call.message.edit_caption(send_msg,
                                     reply_markup=products_open_finl(position_id, remover, category_id))


# Вернуться к позициям для покупки
@dp.callback_query_handler(text_startswith="buy_position_return", state="*")
async def user_purchase_position_return(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    get_positions = get_all_positionsx()

    if len(get_positions) >= 1:
        await call.message.delete()
        await call.message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption="<b>🎁 Выберите нужный вам товар:</b>",
                                  reply_markup=products_item_position_open_fp(remover, category_id, call.from_user.id))
    else:
        await call.message.edit_caption("<b>🎁 Товары в данное время отсутствуют.</b>")
        await call.answer("❗ Позиции были изменены или удалены")


# Следующая страница позиций для покупки
@dp.callback_query_handler(text_startswith="buy_position_nextp", state="*")
async def user_purchase_position_next_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    await call.message.edit_caption("<b>🎁 Выберите нужный вам товар:</b>",
                                 reply_markup=products_item_position_next_page_fp(remover, category_id))


# Предыдущая страница позиций для покупки
@dp.callback_query_handler(text_startswith="buy_position_backp", state="*")
async def user_purchase_position_prev_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    await call.message.edit_text("<b>🎁 Выберите нужный вам товар:</b>",
                                 reply_markup=buy_position_return_page_fp(remover, category_id))


########################################### ПОКУПКА ##########################################
# Выбор количества товаров для покупки
@dp.callback_query_handler(text_startswith="buy_item_select", state="*")
async def user_purchase_select(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])

    get_position = get_positionx(position_id=position_id)
    get_items = get_itemsx(position_id=position_id)
    get_user = get_userx(user_id=call.from_user.id)
    if get_user['user_role'] == "VIP":
        get_position['position_price'] = get_position['position_price'] / 2

    if get_position['position_price'] != 0:
        get_count = int(get_user['user_balance'] / get_position['position_price'])
        if get_count > len(get_items): get_count = len(get_items)
    else:
        get_count = len(get_items)

    if int(get_user['user_balance']) >= int(get_position['position_price']):
        if get_count == 1:
            await state.update_data(here_cache_position_id=position_id)
            await state.finish()

            await call.message.delete()
            await call.message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption=f"<b>🎁 Вы действительно хотите купить товар(ы)?</b>\n"
                                      f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                      f"🎁 Товар: <code>{get_position['position_name']}</code>\n"
                                      f"📦 Количество: <code>1шт</code>\n"
                                      f"💰 Сумма к покупке: <code>{get_position['position_price']}₽</code>",
                                      reply_markup=products_confirm_finl(position_id, 1))
        elif get_count >= 1:
            await state.update_data(here_cache_position_id=position_id)
            await state.set_state("here_item_count")

            await call.message.delete()
            await call.message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption=f"<b>🎁 Введите количество товаров для покупки</b>\n"
                                      f"▶ От <code>1</code> до <code>{get_count}</code>\n"
                                      f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                      f"🎁 Товар: <code>{get_position['position_name']}</code> - <code>{get_position['position_price']}₽</code>\n"
                                      f"💰 Ваш баланс: <code>{get_user['user_balance']}₽</code>")
        else:
            await call.answer("🎁 Товаров нет в наличии")
    else:
        await call.answer("❗ У вас недостаточно средств. Пополните баланс", True)


# Принятие количества товаров для покупки
@dp.message_handler(state="here_item_count")
async def user_purchase_select_count(message: Message, state: FSMContext):
    position_id = (await state.get_data())['here_cache_position_id']

    get_position = get_positionx(position_id=position_id)
    get_user = get_userx(user_id=message.from_user.id)
    get_items = get_itemsx(position_id=position_id)
    if get_user['user_role'] == "VIP":
        get_position['position_price'] = get_position['position_price'] / 2

    if get_position['position_price'] != 0:
        get_count = int(get_user['user_balance'] / get_position['position_price'])
        if get_count > len(get_items): get_count = len(get_items)
    else:
        get_count = len(get_items)

    send_message = f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                   f"🎁 Введите количество товаров для покупки\n" \
                   f"▶ От <code>1</code> до <code>{get_count}</code>\n" \
                   f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                   f"🎁 Товар: <code>{get_position['position_name']}</code> - <code>{get_position['position_price']}₽</code>\n" \
                   f"💰 Ваш баланс: <code>{get_user['user_balance']}₽</code>"

    if message.text.isdigit():
        get_count = int(message.text)
        print(get_position['position_price'])
        amount_pay = int(get_position['position_price'] * get_count)

        if len(get_items) >= 1:
            if 1 <= get_count <= len(get_items):
                if int(get_user['user_balance']) >= amount_pay:
                    await state.finish()
                    await message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption=f"<b>🎁 Вы действительно хотите купить товар(ы)?</b>\n"
                                         f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                         f"🎁 Товар: <code>{get_position['position_name']}</code>\n"
                                         f"📦 Количество: <code>{get_count}шт</code>\n"
                                         f"💰 Сумма к покупке: <code>{amount_pay}₽</code>",
                                         reply_markup=products_confirm_finl(position_id, get_count))
                else:
                    await message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption=f"<b>❌ Недостаточно средств на счете.</b>\n" + send_message)
            else:
                await message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption=f"<b>❌ Неверное количество товаров.</b>\n" + send_message)
        else:
            await state.finish()
            await message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption="<b>🎁 Товар который вы хотели купить, закончился</b>")
    else:
        await message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption=f"<b>❌ Данные были введены неверно.</b>\n" + send_message)


# Подтверждение покупки товара
@dp.callback_query_handler(text_startswith="xbuy_item", state="*")
async def user_purchase_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    position_id = int(call.data.split(":")[2])
    get_count = int(call.data.split(":")[3])

    if get_action == "yes":
        await call.message.edit_caption("<b>🔄 Ждите, товары подготавливаются</b>")

        get_position = get_positionx(position_id=position_id)
        get_items = get_itemsx(position_id=position_id)
        get_user = get_userx(user_id=call.from_user.id)
        if get_user['user_role'] == "VIP":
            get_position['position_price'] = get_position['position_price'] / 2

        amount_pay = int(get_position['position_price'] * get_count)

        if 1 <= int(get_count) <= len(get_items):
            if int(get_user['user_balance']) >= amount_pay:
                save_items, send_count, split_len = buy_itemx(get_items, get_count)

                if get_count != send_count:
                    amount_pay = int(get_position['position_price'] * send_count)
                    get_count = send_count

                receipt = get_unix()
                buy_time = get_date()

                await call.message.delete()
                if split_len == 0:
                    await call.message.answer("\n\n".join(save_items), parse_mode="None")
                else:
                    for item in split_messages(save_items, split_len):
                        await call.message.answer("\n\n".join(item), parse_mode="None")
                        await asyncio.sleep(0.3)

                update_userx(get_user['user_id'], user_balance=get_user['user_balance'] - amount_pay)
                add_purchasex(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt, get_count,
                              amount_pay, get_position['position_price'], get_position['position_id'],
                              get_position['position_name'], "\n".join(save_items), buy_time, receipt,
                              get_user['user_balance'], int(get_user['user_balance'] - amount_pay))

                await call.message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption=f"<b>✅ Вы успешно купили товар(ы)</b>\n"
                                          f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                          f"🧾 Чек: <code>#{receipt}</code>\n"
                                          f"🎁 Товар: <code>{get_position['position_name']} | {get_count}шт | {amount_pay}₽</code>\n"
                                          f"🕰 Дата покупки: <code>{buy_time}</code>",
                                          reply_markup=menu_frep(call.from_user.id))
                if get_user['user_role'] != "VIP" and get_user['user_role'] != "Admin" and get_user['user_role'] != "Buyer":
                    update_userx(user_id=get_user['user_id'], user_role='Buyer')



            else:
                await call.message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption="<b>❗ На вашем счёте недостаточно средств</b>")
        else:
            await call.message.answer_photo(open('tgbot/data/resourses/photo/buy.jpg', 'rb'), caption="<b>🎁 Товар который вы хотели купить закончился или изменился.</b>",
                                      reply_markup=menu_frep(call.from_user.id))
    else:
        if len(get_all_categoriesx()) >= 1:
            await call.message.edit_caption("<b>🎁 Выберите нужный вам товар:</b>",
                                         reply_markup=products_item_category_open_fp(0))
        else:
            await call.message.edit_caption("<b>✅ Вы отменили покупку товаров.</b>")
