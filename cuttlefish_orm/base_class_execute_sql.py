import logging
import sqlite3


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
