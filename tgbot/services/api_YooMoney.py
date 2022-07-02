import random
import string

import requests
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from async_class import AsyncClass
from paymentcheckout import WebMoneyCheck
from os import path

from yoomoney import Client, Quickpay

from tgbot.loader import bot
from tgbot.services.api_sqlite import get_crystal, update_crystal,  get_yoo, update_yoo
from tgbot.services.authorize import Authorize
from tgbot.utils.misc_functions import send_admins


class YooMoneyAPI(AsyncClass):
    async def __ainit__(self, dp, wallet=None, client_id=None, token=None, redirect=None, check_pass=False,
                        add_pass=False):
        if client_id is not None:
            self.client_id = client_id
            self.redirect = redirect
        else:
            self.client_id = get_yoo()['client_id']
            self.redirect = get_yoo()['redirect_uri']
            self.token = get_yoo()['token']
            self.wallet = get_yoo()['wallet']

        self.dp = dp
        self.check_pass = check_pass
        self.add_pass = add_pass
        self.scope= ["account-info",
                               "operation-history",
                               "operation-details",
                               "incoming-transfers",
                               "payment-p2p",
                               "payment-shop",
                               ]

    # Рассылка админам о нерабочем киви
    @staticmethod
    async def error_wallet():
        await send_admins("<b>YooMoney недоступен</b>\n"
                          "❗ Как можно быстрее его замените")

    async def pre_checker(self):
        if self.check_pass:
            if self.token != "None":
                try:
                    client = Client(self.token)
                    user = client.account_info()
                    await self.dp.answer(f"<b>YooMoney полностью функционирует</b>\n"
                                         f"◾ Wallet: <code>{user.account}</code>\n"
                                         f"◾ Токен: <code>{self.token}</code>\n"
                                         f"◾ Идентификатор приложения: <code>{self.client_id}</code>\n")
                except:
                    await self.error_wallet()
                    return False
            else:
                await self.error_wallet()
                return False
        elif self.add_pass:
            try:
                Authoriz = Authorize(
                        client_id=self.client_id,
                        redirect_uri=self.redirect,
                        scope=["account-info",
                               "operation-history",
                               "operation-details",
                               "incoming-transfers",
                               "payment-p2p",
                               "payment-shop",
                               ]
                    )
                token = Authoriz.getToken()
                if token != "GG":
                    update_yoo(wallet=self.wallet, type=self.type, balance=0, status=True)
                    await self.dp.answer("<b>YooMoney был успешно изменён</b>")
                else:
                    await self.dp.answer("<b>YooMoney данные не прошли проверку</b>")
                    return False
            except:
                await self.dp.answer("<b>YooMoney данные не прошли проверку</b>")
                return False
        return True

    # Создание платежа
    async def bill_pay(self, get_amount):
        letters = string.ascii_lowercase
        p = (''.join(random.choice(letters) for i in range(10)))
        print(p)
        quickpay = Quickpay(
            receiver=str(self.wallet),
            quickpay_form="shop",
            targets=self.dp.from_user.username,
            paymentType="SB",
            sum=get_amount,
            label=str(self.dp.from_user.id) + str(get_amount) + str(p)
        )

        return_message = f"🔥 Пополнение баланса\n" \
                         f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                         f"💸 Для пополнения баланса, нажмите на кнопку <code>Перейти к оплате </code>\n" \
                         f"💠 После оплаты, нажмите на кнопку <code>Проверить оплату</code>\n" \
                         f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                         f"💵 Сумма пополнения: {get_amount} RUB\n" \
                         f"⌛️ У вас имеется 30 минут на оплату."
        return quickpay, return_message


    async def get_link(self):
        self.url = "https://yoomoney.ru/oauth/authorize?client_id={client_id}&response_type=code" \
                   "&redirect_uri={redirect_uri}&scope={scope}".format(client_id=self.client_id,
                                                                       redirect_uri=self.redirect,
                                                                       scope='%20'.join(
                                                                           [str(elem) for elem in self.scope]),
                                                                       )

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", self.url, headers=headers)

        if response.status_code == 200:
            return response.url
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Ссылка на авторизацию", url=response.url))
            await self.dp.answer("<b>1) Посетите этот веб-сайт</b> \n"
                                 "<b>2) Подтвердите запрос на авторизацию приложения</b>\n"
                                 "<b>3) После подтверждения отправьте ссылку сайта на который вас перенесли</b>",
                                 reply_markup=keyboard)
        return False


    async def get_token(self, link):
        try:
            code = link[link.index("code=") + 5:].replace(" ","")

        except:
            pass

        url = "https://yoomoney.ru/oauth/token?code={code}&client_id={client_id}&" \
              "grant_type=authorization_code&redirect_uri={redirect_uri}".format(code=str(code),
                                                                                 client_id=self.client_id,
                                                                                 redirect_uri=self.redirect,
                                                                                 )
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        self.response = requests.request("POST", url, headers=headers)
        if "error" in self.response.json():
            return False
        if self.response.json()['access_token'] == "":
            return False


        return self.response.json()['access_token']





    async def get_balance(self):
        try:
            client = Client(self.token)
            user = client.account_info()
            await self.dp.answer(f"<b>🌍 Баланс кошелька <code>{user.account}</code> составляет:</b>\n"
                                 f"🇷🇺 Рублей: <code>{user.balance}₽</code>")
        except:
            await self.error_wallet()
            return False
