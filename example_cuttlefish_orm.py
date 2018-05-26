import sqlite3
from cuttlefish_orm import Base, create_table


class User(Base):
    __tablename__ = 'users'

    # Допустимые типы данных INTEGER, TEXT, BLOB, REAL, NUMERIC
    # Поля БД задаются следующим образом:
    # field_name = ('Type field', 'Options')
    id = ('INTEGER', 'PRIMARY KEY AUTOINCREMENT NOT NULL')
    name = ('TEXT', 'NOT NULL')

    def __init__(self, name):
        self.name = name


def main():
    conn = sqlite3.connect('example.db')
    create_table(conn, User)
    user = User('Vasya')
    user.save(conn)


if __name__ == '__main__':
    main()
