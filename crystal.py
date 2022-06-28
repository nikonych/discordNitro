from pycrystalpay import CrystalPay

# crystal = CrystalPay('nikon','fbee2cde41713ada4c07bfbdf3909b02b8bcf624')


def pre_checker(login, secret):
    if login != "None" and secret != "None":
        try:
            crystal = CrystalPay(login, secret)
            return True
        except:
            return False

print(pre_checker('nikon','fbee2cde41713ada4c07bfbdf3909b02b8bcf624'))
# balance = crystal.get_cash_balance()
# print(balance)
#
# print(crystal)
#
# payment = crystal.create_invoice(100)
# print(payment.url) #Ссылка на оплату
# print(payment.amount) # Сумма к оплате
# print(payment.id) #id оплаты
#
# if payment.if_paid():
#     print(payment.paymethod) # Метод, которым была произведена оплата. "btc", "qiwi"
#     # Оплата была произведена
# else:
#     # Счет не оплачен
#     print(payment.paymethod)