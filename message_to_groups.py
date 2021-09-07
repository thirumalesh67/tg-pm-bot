from telethon.tl.functions.channels import JoinChannelRequest
from setup import DB
from telethon.sync import TelegramClient

db = DB()
sessions = db.get_sessions()

groupUsernames = [
    'testgrp2357',
    'testgroup2332',
]

message = """
Test Message 
in multiple lines
ignore.
"""

for session in sessions:
    try:
        client = TelegramClient(f'sessions/{session[0]}',  3910389 , '86f861352f0ab76a251866059a6adbd6')
        client.start(session[0])
        print(session[0])
        break
    except:
        continue

for group in groupUsernames:
    target = f"https://t.me/{group}"
    client(JoinChannelRequest(target))
    print('Joined the group to Send Message')
    entity = client.get_entity(target)
    client.send_message(target, message)
    print(f'Message sent to Group: {entity.title}')

print('Finished!!!!')

