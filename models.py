import datetime
from peewee import *

db = SqliteDatabase('journal.db')


class Entries(Model):
    id = AutoField()
    title = CharField()
    date = DateTimeField(default=datetime.datetime.now, formats='%Y-%m-%d')
    time_spent = IntegerField()
    learned = CharField()
    resources = CharField()

    class Meta:
        database = db
        order_by = ('-date',)

    @classmethod
    def create_entry(cls, title, date, time_spent, learned, resources):
        new = cls.create(
            title=title,
            date=date,
            time_spent=time_spent,
            learned=learned,
            resources=resources
        )
        return new


def initialize():
    db.connect()
    db.create_tables([Entries, Tags], safe=True)
    db.close()

