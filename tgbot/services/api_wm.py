from aiogram.types import InputFile
from async_class import AsyncClass
from paymentcheckout import WebMoneyCheck
from os import path

from tgbot.loader import bot
from tgbot.services.api_sqlite import get_crystal, update_crystal, get_wm, update_wm
from tgbot.utils.misc_functions import send_admins


class wmAPI(AsyncClass):
    async def __ainit__(self, dp, wallet=None, crt=None, key=None,  check_pass=False,
                        add_pass=False):
        if wallet is not None:
            self.wallet = wallet
            self.crt = crt
            self.key = key
        else:
            self.wallet = get_wm()['wallet']
            self.crt = get_wm()['crt_path']
            self.key = get_wm()['key_path']

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
            if self.wallet != "None" and path.exists(self.crt) and path.exists(self.key):
                try:
                    # w = WebMoneyCheck.WebMoney(self.wallet, self.crt, self.key)
                    await self.dp.answer(f"<b>WebMoney полностью функционирует</b>\n"
                                         f"◾ Wallet: <code>{self.wallet}</code>\n"
                                         f"Сертификаты отправлены ниже:")
                    print(self.crt)
                    await bot.send_document(chat_id=self.dp.chat.id, document=InputFile(self.crt))
                    await bot.send_document(chat_id=self.dp.chat.id, document=InputFile(self.key))
                except:
                    await self.error_wallet()
                    return False
            else:
                await self.error_wallet()
                return False
        elif self.add_pass:
            try:
                # w = WebMoneyCheck.WebMoney(self.wallet, self.crt, self.key)
                # update_wm(wallet=self.wallet, crt_path=self.crt, key_path=self.key, status=True)
                await self.dp.answer("<b>WebMoney был успешно изменён</b>")
            except:
                await self.dp.answer("<b>WebMoney данные не прошли проверку</b>")
                return False

        return True

    # async def get_balance(self):
    #     response = await self.pre_checker()
    #     if response:
    #         crystal = CrystalPay(self.login, self.secret)
    #         balance = crystal.get_cash_balance()
    #         save_balance = []
    #         balance = sorted(balance.items(), key=lambda x: float(x[1]), reverse=True)
    #         for k in balance:
    #             save_balance.append(k[0] + " : " + k[1])
    #         save_balance = "\n".join(save_balance)
    #         await self.dp.answer(f"<b>WebMoney Баланс <code>{self.login}</code> составляет:</b>\n"
    #                              f"{save_balance}")


    # Создание платежа
    async def bill_pay(self, get_amount):
        response = await self.pre_checker()
        if response:
            comment = str(self.dp.from_user_id) + str(get_amount)
            return_message = f"<b>🆙 Пополнение баланса</b>\n" \
                             f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                             f"💎 Для пополнения баланса, отправьте деньги на счет \n <code>{self.wallet}</code> \n с коментарием  \n <code>{comment}</code>\n" \
                             f"💰 Сумма пополнения: <code>{get_amount}₽</code>\n" \
                             f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                             f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
            return comment, return_message

