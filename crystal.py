from yoomoney import Client
from yoomoney import Quickpay
from yoomoney import Client

token = "4100117474341799.B7874FCDAA65571A906154AAFBC9D20CA65E08752031F01C7C546613A69E38367F9C385E1B804A53F5B1D898B9E523E593A559A6A4E6E90B7FE350DB071005A2E89504D3F465D93A357ADE99D1CA711ACF6C7429830DB20789D63D6493AFA3F53FEEDDAB5C8E50A68C69A62036DEEE05BDDF77A9C6597E09BAAF413974DF4987"
client = Client(token)
user = client.account_info()
print("Account number:", user.account)
print("Account balance:", user.balance)
print("Account currency code in ISO 4217 format:", user.currency)
print("Account status:", user.account_status)
print("Account type:", user.account_type)
print("Extended balance information:")
for pair in vars(user.balance_details):
    print("\t-->", pair, ":", vars(user.balance_details).get(pair))
print("Information about linked bank cards:")
cards = user.cards_linked
if len(cards) != 0:
    for card in cards:
        print(card.pan_fragment, " - ", card.type)
else:
    print("No card is linked to the account")

quickpay = Quickpay(
            receiver="410019014512803",
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            sum=150,
            label="a1b2c3d4e5"
            )
print(quickpay.base_url)
print(quickpay.redirected_url)



client = Client(token)
history = client.operation_history(label="a1b2c3d4e5")
print("List of operations:")
print("Next page starts with: ", history.next_record)
for operation in history.operations:
    print()
    print("Operation:",operation.operation_id)
    print("\tStatus     -->", operation.status)
    print("\tDatetime   -->", operation.datetime)
    print("\tTitle      -->", operation.title)
    print("\tPattern id -->", operation.pattern_id)
    print("\tDirection  -->", operation.direction)
    print("\tAmount     -->", operation.amount)
    print("\tLabel      -->", operation.label)
    print("\tType       -->", operation.type)
