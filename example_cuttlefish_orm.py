import sqlite3
from cuttlefish_orm import Base, create_table


class User(Base):
    __tablename__ = 'users'

    # Допустимые типы данных INTEGER, TEXT, BLOB, REAL, NUMERIC
    # Поля БД задаются следующим образом:
    # field_name = ('Type field', 'Options')
    id = ('INTEGER', 'PRIMARY KEY AUTOINCREMENT NOT NULL')
    name = ('TEXT', 'NOT NULL')

    def __init__(self, name, connection_db=None):
        self.name = name
        self.connection_db = connection_db


def main():
    conn = sqlite3.connect('example.db')
    create_table(conn, User)
    user = User('Vasya', conn)
    user.save()
    users_records = User('', conn).select_all()
    print(users_records)
    user_record = User('', conn).select_first()
    print(user_record)
    print(User('', conn).get_fields())

if __name__ == '__main__':
    main()
