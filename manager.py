from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PhoneNumberBannedError
from setup import DB

def manager():
    db = DB()
    print("1. Add New Accounts:")
    print("2. Quit")
    a = int(input("Enter your Choice: "))
    if a==1:
        new_accs = []
        number_of_accs_to_add = int(input("Enter number of accounts to add: "))
        for i in range(number_of_accs_to_add):
            phone_number = str(input("Enter Phone Number: "))
            parsed_number = ''.join(phone_number.split())
            if db.check_account_number(parsed_number):
                print('Account Already registered')
            else:
                new_accs.append(parsed_number)
        print("Logging in from new accounts")
        for number in new_accs:
            c = TelegramClient(f'sessions/{number}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
            c.start(number)
            print(f'Login successful')
            db.create_acccount(number)
            c.disconnect()
        
        print("Accounts succesfully Added")
    elif a==2:
        exit()
    else:
        manager()

manager()