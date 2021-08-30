import sqlite3
from datetime import datetime

conn = sqlite3.connect("tg-bot.db")
# Groups
conn.execute('''
    CREATE TABLE IF NOT EXISTS Groups
    (
        Id INTEGER PRIMARY KEY,
        GroupId TEXT NOT NULL,
        GroupTitle TEXT NOT NULL,
        GroupUserName TEXT NOT NULL,
        GroupAccessHash TEXT NOT NULL,
        CreatedAt TIMESTAMP,
        UpdatedAt TIMESTAMP
    )
''')
# Jobs
conn.execute('''
    CREATE TABLE IF NOT EXISTS JOBs
    (
        JobID INTEGER PRIMARY KEY,
        JobName TEXT NOT NULL,
        GroupId INTEGER,
        GroupName TEXT NOT NULL,
        Message TEXT NOT NULL,
        CreatedAt TIMESTAMP,
        UpdatedAt TIMESTAMP,
        FOREIGN KEY (GroupId) REFERENCES Groups(GroupId)
    )
''')
# Accounts
conn.execute('''
    CREATE TABLE IF NOT EXISTS Accounts
    (
        AccountID INTEGER PRIMARY KEY,
        AccountNumber TEXT NOT NULL,
        CreatedAt TIMESTAMP,
        UpdatedAt TIMESTAMP
    )
''')
# GroupUsers
conn.execute('''
    CREATE TABLE IF NOT EXISTS GroupUsers
    (
        ID INTEGER PRIMARY KEY,
        GroupId INT NOT NULL,
        GroupTitle TEXT NOT NULL,
        UserId TEXT NOT NULL,
        UserName TEXT NOT NULL,
        UserHash TEXT NOT NULL,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        PhoneNumber TEXT NOT NULL,
        CreatedAt TIMESTAMP,
        UpdatedAt TIMESTAMP,
        FOREIGN KEY (GroupId) REFERENCES Groups(Id)
    )
''')
# JobDetails
conn.execute('''
    CREATE TABLE IF NOT EXISTS JobDetails
    (
        ID INTEGER PRIMARY KEY,
        JobID INTEGER,
        GroupId INTEGER,
        UserId TEXT,
        UserName TEXT,
        UserHash TEXT,
        Status TEXT,
        CreatedAt TIMESTAMP,
        UpdatedAt TIMESTAMP,
        FOREIGN KEY (JobID) REFERENCES JOBs(JobID)
    )
''')



conn.commit()




class DB:
    def __init__(self):
        self.conn = sqlite3.connect("tg-bot.db")
        self.cursor = self.conn.cursor()

    def replace_quotes(self,string):
        return str(string).replace('"', '').replace("'","")
        
    def create_job(self, JobName, GroupId, GroupName, Message):
        self.cursor.execute(f'''
            INSERT INTO JOBS (JobName, GroupId, GroupName, Message, CreatedAt, UpdatedAt)
            VALUES ("{self.replace_quotes(JobName)}", {GroupId}, "{self.replace_quotes(GroupName)}", "{self.replace_quotes(Message)}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}" )
        ''')
        inserted_id = self.cursor.lastrowid
        self.conn.commit()
        return inserted_id

    def create_job_details(self, job_id, group_id):
        self.cursor.execute(f'''
            SELECT UserId, UserName, UserHash FROM GroupUsers where GroupId = {group_id}
        ''')
        users = self.cursor.fetchall()
        for user in users:
            user_id = user[0]
            user_name = user[1]
            user_hash = user[2]
            self.conn.execute(f'''
                INSERT INTO JobDetails (JobId, GroupId, UserId, UserName, UserHash, CreatedAt, UpdatedAt)
                VALUES ({job_id}, {group_id}, "{user_id}", "{user_name}", "{user_hash}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}")
            ''')
        self.conn.commit()

    def get_job_to_be_sent_users(self, job_id):
        self.cursor.execute(f'''
            SELECT UserId, UserHash, ID FROM JobDetails WHERE Status IS NULL AND JobID = {job_id}
        ''')
        users = self.cursor.fetchall()
        return users
    
    def update_job_details_user_status(self, jd_id, status):
        self.conn.execute(f'''
            UPDATE JobDetails SET Status = "{self.replace_quotes(status)}" WHERE ID = {jd_id}
        ''')
        self.conn.commit()

    def get_job_details(self, job_id):
        self.cursor.execute(f'''
            SELECT * FROM JOBs where JobId = {job_id}
        ''')
        rows = self.cursor.fetchall()
        return rows

    def create_group(self, GroupId, GroupTitle, GroupUserName, GroupAccessHash):
        self.cursor.execute(f'''
            INSERT INTO Groups (GroupId, GroupTitle, GroupUserName, GroupAccessHash, CreatedAt, UpdatedAt)
            VALUES ("{GroupId}", "{self.replace_quotes(GroupTitle)}", "{GroupUserName}", "{GroupAccessHash}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}")
        ''')
        inserted_id = self.cursor.lastrowid
        self.conn.commit()
        return inserted_id

    def check_account_number(self, PhoneNumber):
        self.cursor.execute(f'''
            SELECT AccountID from Accounts where AccountNumber = "{PhoneNumber}"
        ''')
        rows = self.cursor.fetchall()
        return True if len(rows)>0 else False
    
    def create_acccount(self, AccountNumber):
        self.conn.execute(f'''
            INSERT INTO Accounts(AccountNumber, CreatedAt, UpdatedAt)
            VALUES ("{AccountNumber}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}")
        ''')
        self.conn.commit()
    
    def delete_account(self, AccountNumber):
        self.conn.execute(f'''
            DELETE FROM Account where AccountNumber = "{AccountNumber}"
        ''')
        self.conn.commit()
    
    def get_sessions(self):
        self.cursor.execute('''
            SELECT AccountNumber from Accounts
        ''')
        return self.cursor.fetchall()

    def create_group_users(self, groupId,groupTitle,users):
        for user in users:
            self.conn.execute(f'''
                INSERT INTO GroupUsers (GroupId, GroupTitle, UserId, UserName, UserHash, FirstName, LastName, PhoneNumber, CreatedAt, UpdatedAt)
                VALUES ({groupId}, "{self.replace_quotes(groupTitle)}", "{user.id}", "{user.username}", "{user.access_hash}", "{self.replace_quotes(user.first_name)}", "{self.replace_quotes(user.last_name)}", "{user.phone}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}", "{datetime.now().strftime("%B %d, %Y %I:%M%p")}")
            ''')
        self.conn.commit()
