# - *- coding: utf- 8 - *-
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update

from tgbot.data.config import get_admins
from tgbot.loader import bot
from tgbot.services.api_sqlite import get_userx, add_userx, update_userx, get_settingsx, get_all_users_id
from tgbot.utils.const_functions import clear_html


# Проверка юзеров в БД и его добавление
class ExistsUserMiddleware(BaseMiddleware):
    def __init__(self):
        self.prefix = "key_prefix"
        super(ExistsUserMiddleware, self).__init__()

    async def on_process_update(self, update: Update, data: dict):
        if "message" in update:
            this_user = update.message.from_user
        elif "callback_query" in update:
            this_user = update.callback_query.from_user
        else:
            this_user = None

        if this_user is not None:
            get_settings = get_settingsx()
            get_prefix = self.prefix

            if get_settings['status_work'] == "False" or this_user.id in get_admins():
                if not this_user.is_bot:
                    get_user = get_userx(user_id=this_user.id)

                    user_id = this_user.id
                    user_login = this_user.username
                    user_name = clear_html(this_user.first_name)

                    if user_login is None: user_login = ""

                    if get_user is None:
                        add_userx(user_id, user_login.lower(), user_name)
                        if " " in update.message.text:
                            referrer_candidate = update.message.text.split()[1]
                            try:
                                referrer_candidate = int(referrer_candidate)

                                # Проверяем на несоответствие TG ID пользователя TG ID реферера
                                # Также проверяем, есть ли такой реферер в базе данных
                                if user_id != referrer_candidate and referrer_candidate in get_all_users_id():
                                    referer = referrer_candidate
                                    update_userx(user_id, user_referer=referer)

                            except ValueError:
                                pass
                    else:
                        if user_name != get_user['user_name']:
                            update_userx(get_user['user_id'], user_name=user_name)

                        if len(user_login) >= 1:
                            if user_login.lower() != get_user['user_login']:
                                update_userx(get_user['user_id'], user_login=user_login.lower())
                        else:
                            update_userx(get_user['user_id'], user_login="")
