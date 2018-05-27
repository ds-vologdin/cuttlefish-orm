import sqlite3
from cuttlefish_orm import Base, create_table


class User(Base):
    __tablename__ = 'users'

    # Допустимые типы данных INTEGER, TEXT, BLOB, REAL, NUMERIC
    id = {
        'type': 'INTEGER',
        'options': 'PRIMARY KEY AUTOINCREMENT NOT NULL',
        'column_number': 0
    }
    name = {'type': 'TEXT', 'options': 'NOT NULL', 'column_number': 1}
    email = {'type': 'TEXT', 'options': 'NOT NULL', 'column_number': 2}

    def __init__(self, name, email, connection_db=None):
        self.name = name
        self.email = email
        self.connection_db = connection_db


def main():
    conn = sqlite3.connect('example.db')
    create_table(conn, User)
    user = User('Vasya', 'vasya@mail.ru', conn)
    user.save()
    users_records = User('', '', conn).select_all()
    print(users_records)
    user_record = User('', '', conn).select_first()
    print(user_record)
    print(User('', '', conn).get_fields())

if __name__ == '__main__':
    main()
