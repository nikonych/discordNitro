from paymentcheckout import WebMoneyCheck

#WEBMONEY CONFIG
WEBMONEY_WALLET = "R123456789000" # EXAMPLE
CRT_PATH = "/home/name/crt.pem" # EXAMPLE PATH TO CRT
KEY_PATH = "/home/name/key.pem" # EXAMPLE PATH TO KEY
#WEBMONEY PAY CHECK
WM_PAY_SUM = '1000'
WM_PAY_COMMENT = 'None'

w = WebMoneyCheck.WebMoney(WEBMONEY_WALLET, CRT_PATH, KEY_PATH)
r = w.result_pay(WM_PAY_SUM, WM_PAY_COMMENT)
print(r)
