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

    def __init__(self, name, email, connection_db=None):
        self.name = name
        self.email = email
        self.connection_db = connection_db


class Message(Base):
    __tablename__ = 'articles'

    # Допустимые типы данных INTEGER, TEXT, BLOB, REAL, NUMERIC
    id = {
        'type': 'INTEGER',
        'options': 'PRIMARY KEY AUTOINCREMENT NOT NULL',
        'column_number': 0
    }
    title = {'type': 'TEXT', 'options': 'NOT NULL', 'column_number': 1}
    message = {'type': 'TEXT', 'column_number': 2}
    user_id = {
        'type': 'INTEGER',
        'options': 'NOT NULL',
        'fk': 'articles(id)',
        'column_number': 3,
    }

    def __init__(self, title, message, user_id, connection_db=None):
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
    user = User('Vasya', 'vasya@mail.ru', conn)
    user.save()
    users_records = User('', '', conn).select_all()
    print(users_records)
    user_record = User('', '', conn).select_first()
    print(user_record)
    message = Message(
        'Оповещение',
        'Скорее беги в серверную запускать дизель-генератор',
        user_record[0],
        conn)
    message.save()
    message_record = Message('', '', 0, conn).select_all()
    print(message_record)
    drop_table(conn, User)
    drop_table(conn, Message)


if __name__ == '__main__':
    main()
