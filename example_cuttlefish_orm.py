import sqlite3
import logging
from cuttlefish_orm.base_class import Base
from cuttlefish_orm.db_commands import create_table, drop_table


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
        'model_key': 'Message.id',
        'local_key': 'id',
        'module': 'example_cuttlefish_orm',
    }

    def __init__(self, name='', email='', connection_db=None):
        self.name = name
        self.email = email
        self.connection_db = connection_db
        self.init_relationship()


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
        'model_key': 'User.id',
        'local_key': 'user_id',
        'module': 'example_cuttlefish_orm',
    }

    def __init__(self, title='', message='', user_id=None, connection_db=None):
        self.title = title
        self.message = message
        self.user_id = user_id
        self.connection_db = connection_db
        self.init_relationship()


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

    # SELECT
    user_records = User(connection_db=conn).select_all()
    print('select_all:\n{}'.format(user_records))
    user_record = User(connection_db=conn).select_first()
    print('select_first:\n{}'.format(user_record))

    message = Message(
        'Оповещение',
        'Скорее беги в серверную запускать дизель-генератор',
        user_record[0],
        conn)
    message.save()
    message_record = Message(connection_db=conn).select_all()
    print('select_all:\n{}'.format(message_record))

    # SELECT с задаными полями
    print('='*80)
    fields = ('id', 'email')
    user_records = User(connection_db=conn).select_all(fields)
    print('select_all с заданами параметрами:\n{}'.format(user_records))

    # filter()
    print('='*80)
    user_records = User(connection_db=conn).filter()
    print('filter (select_all):\n{}'.format(user_records))
    user_records = User(connection_db=conn).filter('name = "Vasya"')
    print('filter (select_all):\n{}'.format(user_records))

    # get
    print('='*80)
    # значения ключей обявляются в порядке приоритета column_number
    value_keys_message = (1,)
    user = User(connection_db=conn).get(value_keys_message)
    print('user.name: {}'.format(user.name))

    # relationship
    print('='*80)
    messages = user.messages()
    for message in messages:
        print(message.title)

    print('='*80)
    value_keys_message = (1,)
    message = Message(connection_db=conn).get(value_keys_message)
    print('message.user_id: {}'.format(message.user_id))
    print(message.__dict__)
    user = message.user()
    print('user.name: {}'.format(user[0].name))

    # exception
    user[0].execute_sql_fetch_one('SELECT * FROM table;')

    # drop_table
    drop_table(conn, User)
    drop_table(conn, Message)

if __name__ == '__main__':
    main()
