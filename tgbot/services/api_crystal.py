from async_class import AsyncClass
from pycrystalpay import CrystalPay

from tgbot.services.api_sqlite import get_crystal, update_crystal
from tgbot.utils.misc_functions import send_admins


class CrystalAPI(AsyncClass):
    async def __ainit__(self, dp, login=None, secret=None, check_pass=False,
                        add_pass=False):
        if login is not None:
            self.login = login
            self.secret = secret
        else:
            self.login = get_crystal()['login']
            self.secret = get_crystal()['secret']

        self.dp = dp
        self.check_pass = check_pass
        self.add_pass = add_pass

    # Рассылка админам о нерабочем киви
    @staticmethod
    async def error_wallet():
        await send_admins("<b>💎 Crystal недоступен</b>\n"
                          "❗ Как можно быстрее его замените")


    async def pre_checker(self):
        if self.check_pass:
            if self.login != "None" and self.secret != "None":
                try:
                    crystal = CrystalPay(self.login, self.secret)

                    await self.dp.answer(f"<b>💎 Crystal полностью функционирует</b>\n"
                                         f"◾ Логин: <code>{self.login}</code>\n"
                                         f"◾ Приватный ключ: <code>{self.secret}</code>")
                except:
                    await self.error_wallet()
                    return False
            else:
                await self.error_wallet()
                return False
        elif self.add_pass:
            try:
                test_crystal = CrystalPay(self.login, self.secret)
                update_crystal(login=self.login, secret=self.secret)
                await self.dp.answer("<b>💎 Crystal был успешно изменён</b>")
            except:
                await self.dp.answer("<b>💎 Crystal данные не прошли проверку</b>")
                return False

        return True

    async def get_balance(self):
        response = await self.pre_checker()
        if response:
            crystal = CrystalPay(self.login, self.secret)
            balance = crystal.get_cash_balance()
            save_balance = []
            balance = sorted(balance.items(), key=lambda x: float(x[1]), reverse=True)
            for k in balance:
                save_balance.append(k[0] + " : " + k[1])
            save_balance = "\n".join(save_balance)
            await self.dp.answer(f"<b>💎 Crystal Баланс <code>{self.login}</code> составляет:</b>\n"
                                 f"{save_balance}")


    # Создание платежа
    async def bill_pay(self, get_amount):
        response = await self.pre_checker()
        if response:
            crystal = CrystalPay(self.login, self.secret)
            payment = crystal.create_invoice(get_amount)
            send_requests = payment.url
            return_message = f"<b>🆙 Пополнение баланса</b>\n" \
                             f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                             f"💎 Для пополнения баланса, нажмите на кнопку ниже \n<code>Перейти к оплате</code> и оплатите выставленный вам счёт\n" \
                             f"💰 Сумма пополнения: <code>{get_amount}₽</code>\n" \
                             f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                             f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
            return payment, return_message

