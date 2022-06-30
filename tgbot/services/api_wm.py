from aiogram.types import InputFile
from async_class import AsyncClass
from paymentcheckout import WebMoneyCheck
from os import path

from tgbot.loader import bot
from tgbot.services.api_sqlite import get_crystal, update_crystal, get_wm, update_wm
from tgbot.utils.misc_functions import send_admins


class wmAPI(AsyncClass):
    async def __ainit__(self, dp, wallet=None, type=None, check_pass=False,
                        add_pass=False):
        if wallet is not None:
            self.wallet = wallet
            self.type = type
        else:
            self.wallet = get_wm()['wallet']
            self.type = get_wm()['type']

        self.dp = dp
        self.check_pass = check_pass
        self.add_pass = add_pass

    # Рассылка админам о нерабочем киви
    @staticmethod
    async def error_wallet():
        await send_admins("<b>WebMoney недоступен</b>\n"
                          "❗ Как можно быстрее его замените")

    async def pre_checker(self):
        if self.check_pass:
            if self.wallet != "None":
                try:
                    # w = WebMoneyCheck.WebMoney(self.wallet, self.crt, self.key)
                    await self.dp.answer(f"<b>WebMoney полностью функционирует</b>\n"
                                         f"◾ Wallet: <code>{self.wallet}</code>\n")
                except:
                    await self.error_wallet()
                    return False
            else:
                await self.error_wallet()
                return False
        elif self.add_pass:
            try:
                update_wm(wallet=self.wallet, type=self.type, balance=0, status=True)
                await self.dp.answer("<b>WebMoney был успешно изменён</b>")
            except:
                await self.dp.answer("<b>WebMoney данные не прошли проверку</b>")
                return False

        return True

    # Создание платежа
    async def bill_pay(self, get_amount):
        comment = str(self.dp.from_user.id) + str(get_amount)
        return_message = f"<b>🆙 Пополнение баланса</b>\n" \
                         f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                         f"💎 Для пополнения баланса, отправьте деньги на счет \n <code>{self.wallet}</code> \n с коментарием  \n <code>{comment}</code>\n" \
                         f"💰 Сумма пополнения: <code>{get_amount}₽</code>\n" \
                         f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                         f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
        return comment, return_message

    async def get_balance(self):
        print("gg")
        wm = get_wm()
        balance = wm['balance']
        wallet = wm['wallet']
        await self.dp.answer(f"<b>С момента добавления кошелька <code>{wallet}</code>\n" \
                             f"было зачислено: <code>{balance}</code> </b>")
