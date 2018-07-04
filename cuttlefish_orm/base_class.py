import importlib

from cuttlefish_orm.base_class_execute_sql import BaseExecuteSQL
from cuttlefish_orm.base_class_fields import BaseFields
from cuttlefish_orm.logger import logger


class Base(BaseExecuteSQL, BaseFields):
    ''' Базовый класс cuttlefish_orm '''
    def get(self, keys_value):
        ''' keys_value = (key1_value, key2_value, ...) '''
        primary_keys = self.get_primary_keys()

        if len(keys_value) != len(primary_keys):
            logger.error('Base.get(): len(keys_value) != len(primary_keys)')
            return

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
            logger.error('Base.set_record: len(field_names) != len(values)')
            return
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
        if not result[0]:
            return False
        return True

    def select_all_with_field_names(self, field_names=None):
        if not field_names:
            return
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
            return
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
            return
        sql = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(
            self.__class__.__tablename__,
            ', '.join(fields.keys()),
            ', '.join(fields.values())
        )
        record = self.execute_sql_insert(sql)

        primary_keys = self.get_primary_keys()
        # Сохраняем значение первичных ключей в модели (чаще всего это self.id)
        if len(primary_keys) != len(record):
            logger.error('Base.insert: len(primary_keys) != len(record)')
            return
        for i in range(len(primary_keys)):
            self.__dict__[primary_keys[i]] = record[i]

        return record

    def update(self):
        fields = self.get_fields_with_value_text()
        if not fields:
            return
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
            return
        model_key = name_model_key.split('.')
        if len(model_key) != 2:
            logger.error('Base.parse_name_model_key: len(model_key) != 2')
            return
        return model_key

    def get_class_from_str(self, module, name_class):
        somemodule = importlib.import_module(module)
        return getattr(somemodule, name_class)

    def relationship(self, name_remote_model_key, name_local_key, module):
        # name_remote_model_key 'ClassName.field'
        if not name_remote_model_key:
            return

        remote_model_key = self.parse_name_model_key(name_remote_model_key)
        if not remote_model_key:
            return

        remote_model, remote_key = remote_model_key

        remote_module_class = self.get_class_from_str(module, remote_model)

        local_key_value = self.__dict__.get(name_local_key)

        if not local_key_value:
            return

        local_key_value = local_key_value

        relationship_values = remote_module_class(
            connection_db=self.connection_db
            ).filter(
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
