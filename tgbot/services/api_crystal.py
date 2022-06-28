from async_class import AsyncClass
from pycrystalpay import CrystalPay

from tgbot.services.api_sqlite import get_crystal


class CrystalAPI(AsyncClass):
    async def __ainit__(self, dp, login=None, secret=None, check_pass=False):
        if login is not None:
            self.login = login
            self.secret = secret
        else:
            self.login = get_crystal()['login']
            self.secret = get_crystal()['secret']

        self.dp = dp
        self.check_pass = check_pass


    async def pre_checker(self):
        if self.check_pass:
            if self.login != "None" and self.secret != "None":
                try:
                    crystal = CrystalPay(self.login, self.secret)

                    await self.dp.answer(f"<b>💎 Crystal полностью функционирует</b>\n"
                                         f"◾ Логин: <code>{self.login}</code>\n"
                                         f"◾ Приватный ключ: <code>{self.secret}</code>")
                except:
                    return False
            else:
                return False



