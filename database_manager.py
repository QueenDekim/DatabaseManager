import logging
import sqlite3
import psycopg2
import pymysql
import redis

# Logging setting
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')

class DatabaseManager:
    def __init__(self, db_type: str, db_config: dict):
        """
        Initialization of the database manager.
        :param db_type: Type of database (mysql, postgresql, sqlite, redis).
        :param db_config: Database Configuration.
        """
        self.db_type = db_type.lower()
        self.db_config = db_config
        try:
            self.connection = self._connect()
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            self.connection = None

    def _connect(self):
        """
        Creates a new connection with the database.
        """
        try:
            if self.db_type == 'sqlite':
                return sqlite3.connect(self.db_config['db_name'])
            elif self.db_type == 'postgresql':
                conn = psycopg2.connect(**self.db_config)
                conn.autocommit = True
                return conn
            elif self.db_type == 'mysql':
                return pymysql.connect(
                    user=self.db_config.get('user'),
                    password=self.db_config.get('password'),
                    host=self.db_config.get('host'),
                    database=self.db_config.get('database')
                )
            elif self.db_type == 'redis':
                return redis.Redis(**self.db_config)
            else:
                raise ValueError("Unsupported type of database")
        except ValueError:
            logging.warning(f"Unsupported type of database '{self.db_type}'")
        except Exception as e:
            logging.error(f"Database connection error: {e}")

    def execute(self, method: str, table: str, columns='*', data=None, where: str = None):
        """
        Performs SQL request.
        :param method: Request method (select, insert, update, delete).
        :param table: Table name.
        :param columns: List of columns or string with columns.
        :param data: Request data (list or tuple).
        :param where: The WHERE condition.
        :return: The result of the request.
        """
        try:
            with self._connect() as connection:
                cursor = connection.cursor()

                if self.db_type in ['mysql', 'postgresql']:
                    placeholders = ', '.join(['%s'] * len(data)) if data else ''
                elif self.db_type == 'sqlite':
                    placeholders = ', '.join(['?'] * len(data)) if data else ''

                query = None
                if method.lower() == 'select':
                    query = f"SELECT {', '.join(columns)} FROM {table}"
                elif method.lower() == 'insert':
                    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                elif method.lower() == 'update':
                    set_clause = ', '.join([f"{col} = %s" for col in columns])
                    query = f"UPDATE {table} SET {set_clause}"
                elif method.lower() == 'delete':
                    query = f"DELETE FROM {table}"

                if where:
                    query += f" WHERE {where}"

                if data:
                    cursor.execute(query, tuple(data))
                else:
                    cursor.execute(query)

                if method.lower() == 'select':
                    result = cursor.fetchall()
                    return result
                connection.commit()
                return True
        except Exception as e:
            logging.error(f"Error in performing a database operation: {e}")
            return False

    def _execute_redis(self, method: str, key: str, data=None):
        """
        Performs an operation with Redis.
        :param method: Operation method (select, insert, update, delete).
        :param key: Key in Redis.
        :param data: Data for recording.
        :return: The result of the operation.
        """
        try:
            if method.lower() == 'select':
                return self.connection.get(key)
            elif method.lower() in ['insert', 'update']:
                return self.connection.set(key, data)
            elif method.lower() == 'delete':
                return self.connection.delete(key)
            else:
                raise ValueError("Unsupported method for Redis")
        except Exception as e:
            logging.error(f"Redis operation error: {e}")
            return False

    def close(self):
        """
        Closes the connection with the database.
        """
        try:
            if self.db_type in ['sqlite', 'postgresql', 'mysql'] and self.connection:
                self.connection.close()
        except Exception as e:
            logging.error(f"Error closing the connection with the database: {e}")

    def database_exists(self, database_name: str):
        """
        Checks the existence of a database.
        :param database_name: The name of the database.
        :return: True, if the database exists, otherwise False.
        """
        try:
            if self.db_type == 'mysql':
                cursor = self.connection.cursor()
                cursor.execute(f"SHOW DATABASES LIKE '{database_name}';")
                result = cursor.fetchone() is not None
                cursor.close()
                return result
            elif self.db_type == 'postgresql':
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
                result = cursor.fetchone() is not None
                cursor.close()
                return result
            else:
                raise ValueError("Unsupported type of database to verify the existence of a database")
        except ValueError:
            logging.warning(f"Unsupported type of database '{self.db_type}' to check the existence of a database")
        except Exception as e:
            logging.error(f"Base existence error: {e}")
            return False

    def create_database(self, database_name: str):
        """
        Creates a new database.
        :param database_name: The name of the database.
        """
        try:
            if self.db_type == 'mysql':
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE {database_name};")
                logging.info(f"Database {database_name} successfully created.")
            elif self.db_type == 'postgresql':
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE {database_name};")
                self.connection.commit()
                logging.info(f"Database {database_name} has been successfully created.")
                self.db_config['database'] = database_name
                self.connection.close()
                self.connection = self._connect()
            else:
                raise ValueError("Unsupported type of database for creating a database")
        except ValueError:
            logging.warning(f"Unsupported type of database '{self.db_type}' to create a database")
        except Exception as e:
            logging.error(f"The error of creating a database {database_name}: {e}")

    def table_exists(self, table_name: str):
        """
        Checks the existence of the table.
        :param table_name: Table name.
        :return: True, if the table exists, otherwise False.
        """
        try:
            cursor = self.connection.cursor()
            if self.db_type == 'postgresql':
                cursor.execute("""
                SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = %s AND table_schema = 'public'
                );
                """, (table_name,))
                result = cursor.fetchone()[0]
            elif self.db_type == 'mysql':
                cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = %s AND table_schema = DATABASE();
                """, (table_name,))
                result = cursor.fetchone()[0] > 0
            elif self.db_type == 'sqlite':
                cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?;
                """, (table_name,))
                result = len(cursor.fetchall()) > 0
            else:
                raise ValueError("Unsupported type of database to check the existence of a table")
            cursor.close()
            return result
        except ValueError:
            logging.warning(f"Unfinished type of database '{self.db_type}' to check the existence of a table")
        except Exception as e:
            logging.error(f"The error for checking the existence of the table: {e}")
            return False

    def create_table(self, table_name: str, columns_definition: list):
        """
        Creates a new table.
        :param table_name: Table name.
        :param columns_definition: Determination of table columns.
        """
        try:
            if self.db_type == 'mysql':
                cursor = self.connection.cursor()
                cursor.execute(f"USE {self.db_config.get('database')};")
                cursor.close()
            if self.db_type == 'postgresql':
                cursor = self.connection.cursor()
                query = f"CREATE TABLE {table_name} ({', '.join(columns_definition)})"
                cursor.execute(query)
                self.connection.commit()
                logging.info(f"Table {table_name} successfully created.")
            if self.db_type in ['sqlite', 'mysql']:
                query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_definition)})"
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                logging.info(f"Table {table_name} successfully created.")
        except Exception as e:
            logging.error(f"The error of creating a table {table_name}: {e}")