import logging
import sqlite3
import importlib


class BaseExecuteSQL():
    ''' Класс выполнения sql запросов '''
    def execute_sql_fetch_all(self, sql):
        if not self.connection_db:
            logging.error('connection_db не задано')
            return None
        logging.debug(sql)
        try:
            cursor_db = self.connection_db.cursor()
            cursor_db.execute(sql)
            result = cursor_db.fetchall()
        except sqlite3.Error as e:
            logging.error("sqlite3 error: {}".format(e.args[0]))
            return None
        return result

    def execute_sql_fetch_one(self, sql):
        if not self.connection_db:
            logging.error('connection_db не задано')
            return None
        logging.debug(sql)
        try:
            cursor_db = self.connection_db.cursor()
            cursor_db.execute(sql)
            result = cursor_db.fetchone()
        except sqlite3.Error as e:
            logging.error("sqlite3 error: {}".format(e.args[0]))
            return None
        return result

    def execute_sql(self, sql):
        if not self.connection_db:
            logging.error('connection_db не задано')
            return None
        logging.debug(sql)
        try:
            cursor_db = self.connection_db.cursor()
            cursor_db.execute(sql)
            self.connection_db.commit()
        except sqlite3.Error as e:
            logging.error("sqlite3 error: {}".format(e.args[0]))

    def execute_sql_insert(self, sql_insert):
        if not self.connection_db:
            logging.error('connection_db не задано')
            return None
        logging.debug(sql_insert)
        try:
            cursor_db = self.connection_db.cursor()
            cursor_db.execute(sql_insert)
        except sqlite3.Error as e:
            logging.error("sqlite3 error: {}".format(e.args[0]))
            return None

        sql = 'SELECT last_insert_rowid();'
        logging.debug(sql)
        try:
            cursor_db.execute(sql)
            record = cursor_db.fetchone()
            self.connection_db.commit()
        except sqlite3.Error as e:
            logging.error("sqlite3 error: {}".format(e.args[0]))
            return None
        return record


class BaseFields():
    ''' Класс для работы с полями БД '''
    def get_fields(self):
        class_dict = self.__class__.__dict__
        fields = {
            field_name: field_description
            for field_name, field_description in class_dict.items()
            if is_field_db(field_name, field_description)
        }
        return fields

    def get_field_names(self):
        # Колонки без column_number помещаем в конец таблицы
        def sort_field_by_column_number(x):
            return x[1].get('column_number', 1000)
        fields = sorted(
            self.get_fields().items(),
            key=sort_field_by_column_number
        )
        return [field[0] for field in fields]

    def get_field_type(self, field_name):
        fields = self.get_fields()
        if not fields:
            return None
        if field_name not in fields:
            return None
        field_type = fields[field_name].get('type')
        return field_type

    def get_field_with_value(self):
        field_names = self.get_field_names()
        fields = {
            field_name: self.__dict__[field_name]
            for field_name in field_names
            if field_name in self.__dict__
        }
        return fields

    def get_fields_with_value_text(self):
        fields = self.get_field_with_value()
        for field_name, value in fields.items():
            if self.get_field_type(field_name) == 'TEXT':
                fields[field_name] = '"{}"'.format(value)
            else:
                fields[field_name] = '{}'.format(value)
        return fields

    def is_primary_key_field_description(self, field_description):
        if not field_description:
            return False
        if 'options' not in field_description:
            return False
        if field_description['options'].upper().find('PRIMARY KEY') < 0:
            return False
        return True

    def get_primary_keys(self):
        fields = self.get_fields()

        def sort_field_by_column_number(x):
            return x[1].get('column_number', 1000)
        primary_keys = [
            field_name
            for field_name, field_description in sorted(
                fields.items(),
                key=sort_field_by_column_number
            )
            if self.is_primary_key_field_description(field_description)
        ]
        return primary_keys

    def is_relationship_field(self, field_description):
        if not field_description:
            return None
        if not isinstance(field_description, dict):
            return False
        if field_description.get('type') != 'RELATIONSHIP':
            return None
        return True

    def get_relationship_fields(self):
        class_dict = self.__class__.__dict__
        fields = {
            field_name: field_description
            for field_name, field_description in class_dict.items()
            if self.is_relationship_field(field_description)
        }
        return fields


class Base(BaseExecuteSQL, BaseFields):
    ''' Базовый класс cuttlefish_orm '''
    def get(self, keys_value):
        # keys_value = (key1_value, key2_value, ...)
        primary_keys = self.get_primary_keys()

        if len(keys_value) != len(primary_keys):
            logging.error('Base.get(): len(keys_value) != len(primary_keys)')
            return None

        primary_keys_values_str = [
            '{} = {}'.format(primary_keys[i], keys_value[i])
            for i in range(len(primary_keys))
        ]

        field_names = self.get_field_names()

        sql = 'SELECT {} FROM {} WHERE {};'.format(
            ', '.join(field_names),
            self.__class__.__tablename__,
            ','.join(primary_keys_values_str)
        )
        values = self.execute_sql_fetch_one(sql)

        return self.set_values(values)

    def set_values(self, values):
        field_names = self.get_field_names()
        if len(field_names) != len(values):
            logging.error('Base.set_record: len(field_names) != len(values)')
            return None
        for i in range(len(field_names)):
            self.__dict__[field_names[i]] = values[i]
        return self

    def is_record_in_db(self):
        primary_keys = self.get_primary_keys()
        fields = self.get_fields_with_value_text()
        primary_keys_values_str = []
        for primary_key in primary_keys:
            value = fields.get(primary_key)
            if not value:
                # Если есть не заполненные primary key, значит нет смысла
                # делать запрос в БД
                return False
            primary_keys_values_str.append(
                '{} = {}'.format(
                    primary_key, fields[primary_key]
                )
            )
        sql = 'SELECT count(*) FROM {} WHERE {};'.format(
            self.__class__.__tablename__,
            'AND '.join(primary_keys_values_str)
        )
        result = self.execute_sql_fetch_one(sql)
        if result[0] == 0:
            return False
        return True

    def select_all_with_field_names(self, field_names=None):
        if not field_names:
            return None
        sql = 'SELECT {} FROM {};'.format(
            ', '.join(field_names), self.__class__.__tablename__
        )
        return self.execute_sql_fetch_all(sql)

    def select_all(self, field_names=None):
        if not field_names:
            field_names = self.get_field_names()
        return self.select_all_with_field_names(field_names)

    def select_first_with_field_names(self, field_names=None):
        if not field_names:
            return None
        sql = 'SELECT {} FROM {} LIMIT 1;'.format(
            ', '.join(field_names), self.__class__.__tablename__
        )
        return self.execute_sql_fetch_one(sql)

    def select_first(self, field_names=None):
        if not field_names:
            field_names = self.get_field_names()
        return self.select_first_with_field_names(field_names)

    def insert(self):
        fields = self.get_fields_with_value_text()
        if not fields:
            return None
        sql = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(
            self.__class__.__tablename__,
            ', '.join(fields.keys()),
            ', '.join(fields.values())
        )
        record = self.execute_sql_insert(sql)

        primary_keys = self.get_primary_keys()
        # Сохраняем значение первичных ключей в модели (чаще всего это self.id)
        if len(primary_keys) != len(record):
            logging.error('Base.insert: len(primary_keys) != len(record)')
            return None
        for i in range(len(primary_keys)):
            self.__dict__[primary_keys[i]] = record[i]

        return record

    def update(self):
        fields = self.get_fields_with_value_text()
        if not fields:
            return None
        primary_keys = self.get_primary_keys()
        update_fields_values_str = []
        primary_keys_values_str = []
        for field, value in fields.items():
            if field in primary_keys:
                primary_keys_values_str.append('{} = {}'.format(field, value))
            else:
                update_fields_values_str.append('{} = {}'.format(field, value))
        sql = 'UPDATE {0} SET {1} WHERE {2};'.format(
            self.__class__.__tablename__,
            ', '.join(update_fields_values_str),
            ', '.join(primary_keys_values_str),
        )
        return self.execute_sql(sql)

    def save(self):
        if self.is_record_in_db():
            return self.update()
        return self.insert()

    def filter(self, filter_str=None, field_names=None):
        if not filter_str:
            return self.select_all(field_names)
        if not field_names:
            field_names = self.get_field_names()

        sql = 'SELECT {} FROM {} WHERE {};'.format(
            ', '.join(field_names),
            self.__class__.__tablename__,
            filter_str
        )
        return self.execute_sql_fetch_all(sql)

    def parse_name_model_key(self, name_model_key):
        # name_model_key 'ClassName.field'
        if not name_model_key:
            return None
        model_key = name_model_key.split('.')
        if len(model_key) != 2:
            logging.error('Base.parse_name_model_key: len(model_key) != 2')
            return None
        return model_key

    def get_class_from_str(self, module, name_class):
        somemodule = importlib.import_module(module)
        return getattr(somemodule, name_class)

    def relationship(self, name_remote_model_key, name_local_key, module):
        # name_remote_model_key 'ClassName.field'
        if not name_remote_model_key:
            return None

        remote_model_key = self.parse_name_model_key(name_remote_model_key)
        if not remote_model_key:
            return None

        remote_model, remote_key = remote_model_key

        remote_module_class = self.get_class_from_str(module, remote_model)

        local_key_value = self.__dict__.get(name_local_key)

        if not local_key_value:
            return None

        local_key_value = local_key_value

        relationship_values = \
            remote_module_class(connection_db=self.connection_db).filter(
                '{} = {}'.format(remote_key, local_key_value)
            )

        relationship_modles = [
            remote_module_class(connection_db=self.connection_db).set_values(
                value
            )
            for value in relationship_values
        ]
        return relationship_modles

    def init_relationship(self):
        fields = self.get_relationship_fields()

        for name, description in fields.items():
            self.__dict__[name] = lambda: self.relationship(
                description.get('model_key'),
                description.get('local_key'),
                description.get('module'),
            )


# Функции для работы с БД. Может быть их вынести в отдельный модуль?
def is_field_type_db(type_db):
    type_db = type_db.upper()
    if type_db in ('INTEGER', 'TEXT', 'BLOB', 'REAL', 'NUMERIC'):
        return True
    return False


def is_correct_field_name(field_name):
    if field_name.startswith('__'):
        return False
    return True


def is_corret_field_description(field_description):
    if not isinstance(field_description, dict):
        return False
    # type - обязательный ключ
    if 'type' not in field_description:
        return False
    if not is_field_type_db(field_description['type']):
        return False
    return True


def is_field_db(field_name, field_description):
    ''' field_description = (field_type, field_options)) '''
    if not (field_name and field_description):
        return False
    if not is_correct_field_name(field_name):
        return False
    if not is_corret_field_description(field_description):
        return False
    return True


def get_fields_db_from_class_dict(class_dict):
    class_fields = [
        item for item in class_dict.items()
        if is_field_db(*item)
    ]

    def sort_field_by_column_number(x): return x[1].get('column_number', 1000)
    return sorted(class_fields, key=sort_field_by_column_number)


def get_foreign_keys(fields):
    foreign_keys = [
        (field_name, field_description.get('fk'))
        for field_name, field_description in fields
        if field_description.get('fk')
    ]
    return foreign_keys


def execute_sql(connection_db, sql):
    logging.debug(sql)
    try:
        cursor_db = connection_db.cursor()
        cursor_db.execute(sql)
        connection_db.commit()
    except sqlite3.Error as e:
        logging.error("sqlite3 error: {}".format(e.args[0]))
        return False
    return True


def get_fields_for_create_table(class_fields):
    if not class_fields:
        return None
    return [
        '{} {} {}'.format(
            field_name,
            field_description.get('type'),
            field_description.get('options', ''))
        for field_name, field_description in class_fields
        if is_field_db(field_name, field_description)
    ]


def create_table(connection_db, class_model):
    if not class_model:
        return None

    class_fields_db = get_fields_db_from_class_dict(class_model.__dict__)
    fields = get_fields_for_create_table(class_fields_db)

    sql = 'CREATE TABLE {0} ({1}'.format(
        class_model.__tablename__, ', '.join(fields)
    )

    foreign_keys = get_foreign_keys(class_fields_db)

    for foreign_key in foreign_keys:
        sql = '{}, FOREIGN KEY({}) REFERENCES {}'.format(
            sql, foreign_key[0], foreign_key[1]
            )
    sql = '{});'.format(sql)

    return execute_sql(connection_db, sql)


def create_table_if_not_exist(connection_db, class_model):
    if not class_model:
        return None

    class_fields_db = get_fields_db_from_class_dict(class_model.__dict__)
    fields = get_fields_for_create_table(class_fields_db)

    sql = 'CREATE TABLE IF NOT EXISTS {0} ({1}'.format(
        class_model.__tablename__, ', '.join(fields)
    )
    foreign_keys = get_foreign_keys(class_fields_db)

    for foreign_key in foreign_keys:
        sql = '{}, FOREIGN KEY({}) REFERENCES {}'.format(
            sql, foreign_key[0], foreign_key[1]
            )
    sql = '{});'.format(sql)
    return execute_sql(connection_db, sql)


def drop_table(connection_db, class_model):
    if not class_model:
        return None
    sql = 'DROP TABLE {};'.format(class_model.__tablename__)
    execute_sql(connection_db, sql)
