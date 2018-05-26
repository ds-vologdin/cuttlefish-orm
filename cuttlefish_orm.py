class Base():
    ''' Базовый класс cuttlefish_orm'''
    def select_all(self):
        field_names = [
            k for k in self.__class__.__dict__.keys() if not k.startswith('__')
        ]
        print('SELECT %s FROM %s;' % (
            ', '.join(field_names), self.__class__.__tablename__
        ))

    def save(self, connection_db):
        # field_names = [
        #     key for key in self.__class__.__dict__.keys()
        #     if not key.startswith('__')
        # ]
        # field_values = [
        #     self.__dict__.get(field_name, 'None') for field_name in field_names
        # ]
        # print('INSERT INTO {0} ({1}) VALUES ({2});'.format(
        #     self.__class__.__tablename__,
        #     ', '.join(field_names),
        #     ', '.join(field_values)
        # ))
        columns = {}
        for key, value in self.__dict__.items():
            columns_type = self.__class__.__dict__.get(key)
            if not columns_type:
                continue
            if not is_correct_field_name(key):
                continue
            if columns_type[0] == "TEXT":
                columns[key] = '"{}"'.format(value)
            else:
                columns[key] = '{}'.format(value)
        if not columns:
            return None
        sql = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(
            self.__class__.__tablename__,
            ', '.join(columns.keys()),
            ', '.join(columns.values())
        )
        print(sql)
        cursor_db = connection_db.cursor()
        cursor_db.execute(sql)
        connection_db.commit()


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
    if not len(field_description) == 2:
        return False
    field_type, field_options = field_description
    if not is_field_type_db(field_type):
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


def create_table(connection_db, class_model):
    if not class_model:
        return None

    class_fields = class_model.__dict__

    fields = [
        '{} {}'.format(field_name, ' '.join(field_description))
        for field_name, field_description in class_fields.items()
        if is_field_db(field_name, field_description)
    ]

    sql = 'CREATE TABLE {0} ({1});'.format(
        class_model.__tablename__, ', '.join(fields)
    )
    print(sql)
    cursor_db = connection_db.cursor()
    cursor_db.execute(sql)
    connection_db.commit()
