from telethon.hints import Username
from setup import DB
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import MegagroupIdInvalidError, PeerFloodError, UserPrivacyRestrictedError, PhoneNumberBannedError, ChatAdminRequiredError
from telethon.errors.rpcerrorlist import ChatWriteForbiddenError, UserBannedInChannelError, UserAlreadyParticipantError, FloodWaitError
from telethon.tl.functions.channels import InviteToChannelRequest
import sys
from telethon.tl.functions.messages import ImportChatInviteRequest, AddChatUserRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import UserStatusRecently
import time


db = DB()
sessions = db.get_sessions()
peerErrorCount = 0

if len(sessions) == 0:
    print(f'No Active Sessions, Create Session using manager.py program')
    exit()

print('Checking for Active Sessions')
# Checking for Banned Accounts
for a in sessions:
    phn = a[0]
    print(f'Checking {phn}')
    clnt = TelegramClient(f'sessions/{phn}', 3910389, '86f861352f0ab76a251866059a6adbd6')
    clnt.connect()
    banned = []
    if clnt.is_user_authorized():
        print(f"{phn} session Active")
    elif not clnt.is_user_authorized():
        try:
            clnt.send_code_request(phn)
            print('OK')
        except PhoneNumberBannedError:
            print(f'{phn} is banned!')
            banned.append(a)
    for z in banned:
        db.delete_account(z)
        print('Banned account removed')
    time.sleep(0.5)
    clnt.disconnect()

def get_message(group_id, group_title):
    message = str(input("Enter the Message to be sent: "))
    job_id = db.create_job(f"Message to Group Users {group_title}", group_id,group_title,message)

    print(f"\nJob Created to Send message to Group Users {group_title}\n")
    print(f"Refer to the Job Id: {job_id} for resuming the job later.")
    db.create_job_details(job_id, group_id)
    send_message_pre(job_id)

def get_active_clients():
    clients = []
    for session in sessions:
        try:
            c = TelegramClient(f'sessions/{session[0]}',  3910389 , '86f861352f0ab76a251866059a6adbd6')
            c.start(session[0])
            clients.append(c)
        except:
            continue
    return clients

def send_message_pre(job_id):
    job_details = db.get_job_details(job_id)
    if len(job_details) == 0:
        print('Invalid Job ID')
        exit()
    message = job_details[0][4]
    users = db.get_job_to_be_sent_users(job_id)
    clients = get_active_clients()
    users_per_client = int(len(users)/len(clients))
    for i in range(len(clients)+1):
        if i == len(clients):
            client = clients[i-1]
        else:
            client = clients[i]
        global peerErrorCount
        if peerErrorCount >=10 and i == len(clients):
            print(f'Peer Flood Error for more than 10 users, Try Later resuming the Job with Job Id: {job_id}')
            client.disconnect()
            sys.exit()
        elif peerErrorCount >=10:
            peerErrorCount = 0
            client.disconnect()
            continue
       
        thread_handler_with_users(users[i*users_per_client: (i*users_per_client)+users_per_client], message, client, job_id)



def thread_handler_with_users(users, message, client, job_id):
    for user in users:    
        user_id = int(user[0])
        user_hash = int(user[1])
        jd_id = user[2]
        receiver = InputPeerUser(user_id, user_hash)
        status = send_message(receiver, message, client)
        db.update_job_details_user_status(jd_id, status)
        print('Sleeping 15 secs')
        time.sleep(15)
    return True


def send_message(receiver,message,client):
    try:
        client.send_message(receiver, message)
        return 'Success'
    except PeerFloodError:
        global peerErrorCount
        peerErrorCount = peerErrorCount + 1
        return 'PeerFloodError'
    except Exception as e:
        return e


def app():
    print("1. Send Message to Users in a Group")
    print("2. Resume a Job")

    i = int(input("Enter your choice: "))

    if i == 1:
        print("\n\n")
        print("Choose an Option")
        print("1. Public Group")
        print("2. Private Group")
        choice = int(input("Enter Choice: "))
        if choice == 1:
            target = str(input('Enter public group link: '))
        elif choice == 2:
            target = str(input('Enter private group link: '))
        else:
            print('Invalid Choice')
            app()
        
        c = TelegramClient(f'sessions/{sessions[0][0]}',  3910389 , '86f861352f0ab76a251866059a6adbd6')
        c.start(sessions[0][0])
        try:
            if '/joinchat/' in target:
                g_hash = target.split('/joinchat/')[1]
                try:
                    c(ImportChatInviteRequest(g_hash))
                    print('Joined the group to Download Users')
                except UserAlreadyParticipantError:
                    pass
            else:
                c(JoinChannelRequest(target))
                print('Joined the group to Download Users')
            target_entity = c.get_entity(target)
            groupId=db.create_group(target_entity.id, target_entity.title, target_entity.username, target_entity.access_hash)
            users = []
            users = c.get_participants(target_entity, aggressive=True)
            c.disconnect()
            db.create_group_users(groupId, target_entity.title, users)
            print('Users Downloaded to DB.')
            get_message(groupId, target_entity.title)
        except Exception as e:
            print('Couldnt download users. Check the Group Url')
            print(e)
            exit()
    elif i == 2:
        job_id = input("\nEnter the Job_Id: ")
        send_message_pre(job_id)
    else:
        print('Invalid Choice')
        app()

app()