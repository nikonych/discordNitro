# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Рассылка
ad_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("✅ Отправить", callback_data="confirm_ad:yes"),
    InlineKeyboardButton("❌ Отменить", callback_data="confirm_ad:not")
)

# Кнопки при поиске профиля через админ-меню
profile_open_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("💰 Пополнить", callback_data="user_refill"),
    InlineKeyboardButton("🎁 Мои покупки", callback_data="user_history"),

)
profile_open_inl.add(
    InlineKeyboardButton("🤑 Реферальная система", callback_data="user_referer")
)


# Удаление сообщения
close_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("❌ Закрыть", callback_data="close_this"),
)


close_referer = InlineKeyboardMarkup(

).add(
    InlineKeyboardButton("⬅ Вернуться ↩", callback_data="user_profile")
)

######################################## ТОВАРЫ ########################################
# Удаление категорий
category_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("✅ Да, удалить все", callback_data="confirm_remove_category:yes"),
    InlineKeyboardButton("❌ Нет, отменить", callback_data="confirm_remove_category:not")
)

# Удаление позиций
position_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("✅ Да, удалить все", callback_data="confirm_remove_position:yes"),
    InlineKeyboardButton("❌ Нет, отменить", callback_data="confirm_remove_position:not")
)

# Удаление товаров
item_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("✅ Да, удалить все", callback_data="confirm_remove_item:yes"),
    InlineKeyboardButton("❌ Нет, отменить", callback_data="confirm_remove_item:not")
)
