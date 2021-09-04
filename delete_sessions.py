import sqlite3
from telethon.sync import TelegramClient

conn = sqlite3.connect("tg-bot.db")
from setup import DB

db = DB()
sessions = db.get_sessions()

for a in sessions:
    phn = a[0]
    print(f'Checking {phn}')
    clnt = TelegramClient(f'sessions/{phn}', 3910389, '86f861352f0ab76a251866059a6adbd6')
    clnt.connect()
    banned = []
    if clnt.is_user_authorized():
        print(f"{phn} session Active")
        clnt.disconnect()
    elif not clnt.is_user_authorized():
        db.delete_account(phn)


