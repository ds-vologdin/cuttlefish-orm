# cuttlefish-orm
ORM для работы с sqlite3. Задумывалась для работы в связке с [cuttlefish-web-framework](https://github.com/ds-vologdin/cuttlefish-web-framework) ;)

Шутка, это учебный проект, представляющий интерес исключительно в академических целях.

**Не рекомендую использовать в боевых условиях!**

## Установка
```
git clone https://github.com/ds-vologdin/cuttlefish-orm.git
```
Библиотека работает без использования внешних (не входящих в python) библиотек.

## Использование
Пример использования приведён в [example_cuttlefish_orm.py](https://github.com/ds-vologdin/cuttlefish-orm/blob/master/example_cuttlefish_orm.py)

Для начала имортируем модуль cuttlefish_orm и 
```
from cuttlefish_orm import Base, create_table, drop_table
```

Создаём модели данных
```
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
        # 'module': __file__[:-3],
    }

    def __init__(self, name='', email='', connection_db=None):
        self.name = name
        self.email = email
        self.connection_db = connection_db
        self.init_relationship()
```
Переменная ```__tablename__ ``` задаёт имя таблицы в БД.
Все переменные класса, представлющие собой словарь вида
```
{
    'type': 'TYPE_FIELD',
    'options': 'OPTIONS_FILED',
    'column_number': PRIORITY,
}
```
мапятся в БД.

Допустимые значения 'type': INTEGER, TEXT, BLOB, REAL, NUMERIC (стандартные sqlite3).

options - опции типа в терминах БД (в нашем случае sqlite3)

column_number задаёт приоритет размещения колонок в БД. Чем ниже число, тем выше приоритет. Поля с незаданным приоритетом располагаются в конце списка в случайном порядке.

Есть особый тип **RELATIONSHIP**, он описывает связи в таблицах. При этом обязательно нужно задать значения

 - model_key (название переменной класса - модели, с которой формируется связь)
 - local_key (название локальной переменной, по которой осуществялется связь)
 - module (название вашего модуля, в котором объявлен класс из model_key, можно воспользоваться значением ```__file__```)

### Создание и удаление таблицы
```
conn = sqlite3.connect('example.db')
create_table(conn, User)
drop_table(conn, User)
```
### INSERT и UPDATE записей в БД
```
# INSERT
user = User('Vasya', 'vasya@mail.ru', conn)
user.save()

# UPDATE
user.email = 'vasya@gmail.com'
user.save()
```
### SELECT
Возвращает сырые данные (не экземпляры объектов!!!)
```
user_records = User(connection_db=conn).select_all()
print('select_all:\n{}'.format(user_records))
user_record = User(connection_db=conn).select_first()
print('select_first:\n{}'.format(user_record))
```
### FILTER
Возвращает сырые данные (не экземпляры объектов!!!)
```
user_records = User(connection_db=conn).filter('name = "Vasya"')
```
### GET
Возвращает экземпляры объектов
```
value_keys_message = (1,)
user = User(connection_db=conn).get(value_keys_message)
print('user.name: {}'.format(user.name))
```
value_keys_message задаются в порядке их приоритета, заданного в модели как ```column_number```.

### Работа с relationship
При обращении к полю relationship будет получен результат в виде списка экземпляров класса связанной модели. На самом деле это поле представляет из себя lambda функцию, поэтому вызывать его надо соответсвующе (как функцию - со скобочками)
```
messages = user.messages()
for message in messages:
    print(message.title)
```
