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
    user_id = ForeignKeyField(User, related_name='user', rel_model=User)
    title = CharField(unique=True)
    date = DateTimeField(default=datetime.datetime.now, formats='%Y-%m-%d')
    time_spent = IntegerField()
    learned = TextField()
    resources = TextField()

    class Meta:
        database = db
        order_by = ('-date',)

    @classmethod
    def create_entry(cls, title, date, time_spent, learned, resources):
        try:
            with db.transaction():
                cls.create(
                    title=title,
                    date=date,
                    time_spent=time_spent,
                    learned=learned,
                    resources=resources
                )
        except IntegrityError:
            raise ValueError('This post already exists!')

    def get_user_posts(self):
        return Entries.select().where(Entries.user_id == self)

    def get_tags(self):
        return Tags.select().join(
            on=TagPostRel.to_tag
        ).where(TagPostRel.from_entry == self)


class Tags(Model):
    tag_name = CharField(unique=True)

    class Meta:
        database = db

    @classmethod
    def create_tag(cls, tag_name):
        with db.transaction():
            try:
                cls.create(
                    tag=tag_name
                )
            except IntegrityError:
                raise ValueError('this tag already exists')

    def get_entries(self):
        return Entries.select().join(
            TagPostRel,
            on=TagPostRel.from_entry).where(
            TagPostRel.to_tag == self)


class TagPostRel(Model):
    from_entry = ForeignKeyField(Entries)
    to_tag = ForeignKeyField(Tags)

    class Meta:
        database = db
        indexes = (
            (('from_entry', 'to_tag'), True),)

    @classmethod
    def create_rel(cls, from_entry, to_tag):
        try:
            with db.transaction():
                cls.create(
                    from_entry=from_entry,
                    to_tag=to_tag
                )
        except IntegrityError:
            raise ValueError('relationship already exists')


def initialize():
    db.connect()
    db.create_tables([User, Entries, Tags, TagPostRel], safe=True)
    db.close()

