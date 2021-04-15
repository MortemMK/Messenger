import datetime
from peewee import *

from PyQt5 import QtCore

mainDatabase = SqliteDatabase(None)
print(mainDatabase)

class Msg:
    def __init__(self, msg=None, text=None, img=None, f=None, date=None, m_id=None, replay=None, avatar=None, sender = None):
        self.text = text
        self.img = img
        self.f = f
        self.avatar = avatar
        self.date = date
        self.sender = sender

        if self.date == None:
            self.date = QtCore.QDateTime.currentDateTime()
        self.m_id = m_id
        self.replay = replay
        if msg != None:
            self.text = msg.text
            self.img = msg.img
            self.f = msg.f
            self.date = QtCore.QDateTime(msg.date)
            self.m_id = msg.id
            self.replay = Msg(replay)
            self.sender = msg.sender
            self.avatar = DBAccount.select().where(DBAccount.id == self.sender).get().avatar


    def is_text(self):
        return self.text != None

    def is_img(self):
        return self.img != None

    def is_f(self):
        return self.f != None and self.f
    
    def __str__(self):
        res = ''
        if self.m_id != None:
            res += str(self.m_id) + ' '
        if self.text != None:
            res += self.text + ' '
        if self.replay != None:
            res += '/ ' + str(self.replay) + ' '
        return res


class BaseModel(Model):
    class Meta:
        database = mainDatabase


class DBAccount(BaseModel):
    name = CharField(unique = True)
    avatar = CharField(null = True)


class DBDialog(BaseModel):
    date = DateTimeField(default=datetime.datetime.now)
    account = ForeignKeyField(DBAccount)


class DBMessage(BaseModel):
    text = CharField(null = True)
    img = CharField(null = True)
    f = BooleanField(default = True)
    sender = CharField(null = True)
    date = DateTimeField(default=datetime.datetime.now)
    dialog = ForeignKeyField(DBDialog)
    replay = ForeignKeyField('self', null = True)


def initDatabase0():
    user_a = DBAccount.create(name="My_name", avatar=None)


def initDatabase1():
    user_a = DBAccount.create(name="Krosh", avatar="avatars/krosh.jpg")
    dialog_a = DBDialog.create(account=user_a, date=datetime.datetime(2020, 2, 1, 12, 0))
    msg_a = DBMessage.create(text="Have you ever been in Sochi?", date=datetime.datetime(2020, 2, 1, 12, 0), f=True, dialog=dialog_a, sender = DBAccount.select().where(DBAccount.name == "Krosh").get().id)


def initDatabase2():
    user_a = DBAccount.create(name="Ejik", avatar="avatars/ejik.jpg")
    dialog_a = DBDialog.create(account=user_a, date=datetime.datetime(2020, 2, 1, 13, 0))
    msg_a = DBMessage.create(text="Hello, world!", date=datetime.datetime(2020, 2, 1, 13, 0), f=True, dialog=dialog_a, sender = DBAccount.select().where(DBAccount.name == "Ejik").get().id)


def initDatabase():
    initDatabase0()
    initDatabase1()
    initDatabase2()


class MyDataBase:
    def __init__(self, name):
        mainDatabase.init(name)
        mainDatabase.connect()
        mainDatabase.create_tables(BaseModel.__subclasses__())
        try:
            initDatabase()
        except IntegrityError:
            print("database init canceled")


    def add_dialog(self, img=None, name=''):
        try:
            acc = DBAccount.create(name=name, avatar=img)
            d = DBDialog.create(account=acc)
            m = DBMessage.create(text=f'Hello, Im {name}!', dialog=d, f=True, sender = DBAccount.select().where(DBAccount.name == name).get().id)
        except:
            print("Account with name(", name, ") already exists")

    def dialogs(self):
        tmp = [(i, Msg(msg=DBMessage.select().where(i.id == DBMessage.dialog).order_by(DBMessage.date.desc()).get())) for i in DBDialog.select()]
        tmp = sorted(tmp, key=lambda x : x[1].date)
        for idx, _ in enumerate(tmp):
            tmp[idx][1].replay = None
        return tmp[::-1]

    def add_msg(self, d_id, msg):
        replay = None
        if msg.replay:
            replay = msg.replay.m_id
        f = msg.is_f()
            
        if msg.is_text():
            DBMessage.create(text=msg.text, f=f, dialog=DBDialog.get_by_id(d_id), replay=replay, sender = msg.sender)#, sender = send_id)
        if msg.is_img():
            DBMessage.create(img=msg.img, f=f, dialog=DBDialog.get_by_id(d_id), replay=replay, sender = msg.sender)

    def messages(self, d_id):
        tmp = {i : Msg(msg=i) for i in DBMessage.select().join(DBDialog).where(DBDialog.id == d_id)}
        def add_replay(db_m, m):
            if db_m.replay != None:
                tmp_db_m = DBMessage.get_by_id(db_m.replay)
                m.replay = add_replay(tmp_db_m, Msg(msg=tmp_db_m))
            else:
                m.replay = None
            return m
        return [add_replay(k, i) for k, i in tmp.items()]

    def my_profile(self, name='', img=None):
        q = DBAccount.select().where(DBAccount.id == 1).get()
        q.name = name
        q.avatar = img
        q.save()


