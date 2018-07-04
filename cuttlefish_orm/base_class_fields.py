from cuttlefish_orm.db_commands import is_field_db


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
