import sqlite3

from cuttlefish_orm.logger import logger


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
    logger.debug(sql)
    try:
        cursor_db = connection_db.cursor()
        cursor_db.execute(sql)
        connection_db.commit()
    except sqlite3.Error as e:
        logger.error("sqlite3 error: {}".format(e.args[0]))
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
