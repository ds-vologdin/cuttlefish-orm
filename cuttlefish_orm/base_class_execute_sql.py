from cuttlefish_orm.logger import logger
from cuttlefish_orm.db_commands import catch_sqlite3_exceptions


class BaseExecuteSQL():
    ''' Класс выполнения sql запросов '''

    def _execute_sql_without_commit(self, sql):
        ''' Возвращает курсор БД '''
        if not self.connection_db:
            logger.error('connection_db не задано')
            return None
        logger.debug(sql)
        cursor_db = self.connection_db.cursor()
        cursor_db.execute(sql)
        return cursor_db

    @catch_sqlite3_exceptions
    def execute_sql_fetch_all(self, sql):
        cursor_db = self._execute_sql_without_commit(sql)
        return cursor_db.fetchall() if cursor_db else None

    @catch_sqlite3_exceptions
    def execute_sql_fetch_one(self, sql):
        cursor_db = self._execute_sql_without_commit(sql)
        return cursor_db.fetchone() if cursor_db else None

    @catch_sqlite3_exceptions
    def execute_sql(self, sql, commit=True):
        cursor_db = self._execute_sql_without_commit(sql)
        if cursor_db and commit:
            self.connection_db.commit()

    @catch_sqlite3_exceptions
    def execute_sql_insert(self, sql_insert):
        cursor_db = self._execute_sql_without_commit(sql_insert)
        if not cursor_db:
            return None

        sql = 'SELECT last_insert_rowid();'
        logger.debug(sql)

        cursor_db.execute(sql)
        record = cursor_db.fetchone()
        self.connection_db.commit()
        return record
