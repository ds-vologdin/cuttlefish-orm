import sqlite3
import logging
from cuttlefish_orm import Base, create_table, drop_table


class User(Base):
    __tablename__ = 'users'

    # Допустимые типы данных INTEGER, TEXT, BLOB, REAL, NUMERIC
    id = {
        'type': 'INTEGER',
        'options': 'PRIMARY KEY AUTOINCREMENT NOT NULL',
        'column_number': 0,
    }
    name = {'type': 'TEXT', 'options': 'NOT NULL', 'column_number': 1}
    email = {'type': 'TEXT', 'options': 'NOT NULL', 'column_number': 2}
    messages = {
        'type': 'RELATIONSHIP',
        'model': 'Message',
        'back_populates': 'user',
    }

    def __init__(self, name='', email='', connection_db=None):
        self.name = name
        self.email = email
        self.connection_db = connection_db


class Message(Base):
    __tablename__ = 'messages'

    # Допустимые типы данных INTEGER, TEXT, BLOB, REAL, NUMERIC
    id = {
        'type': 'INTEGER',
        'options': 'PRIMARY KEY AUTOINCREMENT NOT NULL',
        'column_number': 0,
    }
    title = {'type': 'TEXT', 'options': 'NOT NULL', 'column_number': 1}
    message = {'type': 'TEXT', 'column_number': 2}
    user_id = {
        'type': 'INTEGER',
        'options': 'NOT NULL',
        'fk': 'articles(id)',
        'column_number': 3,
    }
    user = {
        'type': 'RELATIONSHIP',
        'model': 'User',
        'back_populates': 'messages',
    }

    def __init__(self, title='', message='', user_id=None, connection_db=None):
        self.title = title
        self.message = message
        self.user_id = user_id
        self.connection_db = connection_db


def main():
    logging.basicConfig(
        filename=None,
        level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    conn = sqlite3.connect('example.db')
    create_table(conn, User)
    create_table(conn, Message)

    # INSERT
    user = User('Vasya', 'vasya@mail.ru', conn)
    user.save()
    # UPDATE
    user.email = 'vasya@gmail.com'
    user.save()

    user_records = User('', '', conn).select_all()
    print('select_all:\n{}'.format(user_records))
    user_record = User('', '', conn).select_first()
    print('select_first:\n{}'.format(user_record))
    # SELECT с задаными полями
    fields = ('id', 'email')
    user_records = User('', '', conn).select_all(fields)
    print('select_all с заданами параметрами:\n{}'.format(user_records))
    # filter()
    user_records = User('', '', conn).filter()
    print('filter (select_all):\n{}'.format(user_records))
    user_records = User('', '', conn).filter('name = "Vasya"')
    print('filter (select_all):\n{}'.format(user_records))

    message = Message(
        'Оповещение',
        'Скорее беги в серверную запускать дизель-генератор',
        user_record[0],
        conn)
    message.save()
    message_record = Message('', '', 0, conn).select_all()
    print(message_record)

    # get
    keys_value = (1,)
    user = User('', '', conn).get(keys_value)
    print(user.name)

    # relationship
    messages = user.relationship('Message.id', 'id', __file__[:-3])
    for message in messages:
        print(message.title)

    # drop_table(conn, User)
    # drop_table(conn, Message)


if __name__ == '__main__':
    main()
