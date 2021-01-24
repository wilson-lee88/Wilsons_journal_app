import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin, current_user
from peewee import *

db = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    user_name = CharField(max_length=30, unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = db

    @classmethod
    def create_user(cls, username, password, admin=False):
        try:
            cls.create(
                user_name=username,
                password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError('User already exists!')


class Entries(Model):
    id = AutoField()
    user_id = ForeignKeyField(User)
    title = CharField()
    date = DateTimeField(default=datetime.datetime.now, formats='%Y-%m-%d')
    time_spent = IntegerField()
    learned = CharField()
    resources = CharField()

    class Meta:
        database = db
        order_by = ('-date',)

    @classmethod
    def create_entry(cls, user_id, title, date, time_spent, learned, resources):
        cls.create(
            user_id=user_id,
            title=title,
            date=date,
            time_spent=time_spent,
            learned=learned,
            resources=resources
        )

    def tags(self):
        return Tags.select().join(
            TagEntryRel,
            on=TagEntryRel.to_tag).where(
            TagEntryRel.from_entry == self
        )


class Tags(Model):
    tag_name = CharField()

    class Meta:
        database = db
        order_by = ('-date',)

    @classmethod
    def create_tag(cls, tag_name):
        cls.create(
            tag_name=tag_name
        )


class TagEntryRel(Model):
    from_entry = ForeignKeyField(Entries)
    to_tag = ForeignKeyField(Tags)

    class Meta:
        database = db

    @classmethod
    def create_rel(cls, entry, tag):
        cls.create(
            from_entry=entry,
            to_tag=tag
        )


def initialize():
    db.connect()
    db.create_tables([User, Entries, Tags, TagEntryRel], safe=True)
    db.close()

