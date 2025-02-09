import logging
import sqlite3
import psycopg2
import pymysql
import redis

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')

# Database manager class
class DatabaseManager:
    def __init__(self, db_type, db_config):
        self.db_type = db_type.lower()
        self.db_config = db_config
        try:
            self.connection = self._connect()
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            self.connection = None

    def _connect(self):
        try:
            if self.db_type == 'sqlite':
                return sqlite3.connect(self.db_config['db_name'])
            elif self.db_type == 'postgresql':
                # Enable autocommit mode for PostgreSQL connections
                conn = psycopg2.connect(**self.db_config)
                conn.autocommit = True  # Ensure autocommit is always enabled for PostgreSQL
                return conn
            elif self.db_type == 'mysql':
                return pymysql.connect(
                    user=self.db_config.get('user'),
                    password=self.db_config.get('password'),
                    host=self.db_config.get('host'),
                    database=self.db_config.get('database')  # Use the specified database
                )
            elif self.db_type == 'redis':
                return redis.Redis(**self.db_config)
            else:
                raise ValueError("Unsupported database type")

        except ValueError:
            logging.warning(f"Unsupported database type '{self.db_type}' for database creation")
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")

    def execute(self, method, table, columns='*', data=None, where=None):
        try:
            if self.db_type == 'redis':
                return self._execute_redis(method, table, data)
            cursor = self.connection.cursor()
            query = ""
            if method.lower() == 'select':
                query = f"SELECT {', '.join(columns)} FROM {table}"
                if where:
                    query += f" WHERE {where}"
                cursor.execute(query)
                result = cursor.fetchall()
                return result
            elif method.lower() == 'insert':
                placeholders = ', '.join(['%s'] * len(data))
                query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(query, tuple(data))
            elif method.lower() == 'update':
                set_clause = ', '.join([f"{col} = %s" for col in columns])
                query = f"UPDATE {table} SET {set_clause}"
                if where:
                    query += f" WHERE {where}"
                cursor.execute(query, tuple(data))
            elif method.lower() == 'delete':
                query = f"DELETE FROM {table}"
                if where:
                    query += f" WHERE {where}"
                cursor.execute(query)
            else:
                raise ValueError("Unsupported method")
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logging.error(f"Error executing database operation: {e}")
            return False

    def _execute_redis(self, method, key, data=None):
        try:
            if method.lower() == 'select':
                return self.connection.get(key)
            elif method.lower() == 'insert':
                return self.connection.set(key, data)
            elif method.lower() == 'update':
                return self.connection.set(key, data)
            elif method.lower() == 'delete':
                return self.connection.delete(key)
            else:
                raise ValueError("Unsupported method for Redis")
        except Exception as e:
            logging.error(f"Error executing Redis operation: {e}")
            return False

    def close(self):
        try:
            if self.db_type in ['sqlite', 'postgresql', 'mysql'] and self.connection:
                self.connection.close()
        except Exception as e:
            logging.error(f"Error closing database connection: {e}")

    # Method to check if a database exists
    def database_exists(self, database_name):
        try:
            if self.db_type == 'mysql':
                cursor = self.connection.cursor()
                cursor.execute(f"SHOW DATABASES LIKE '{database_name}';")
                result = cursor.fetchone() is not None
                cursor.close()
                return result
            elif self.db_type == 'postgresql':
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM pg_database
                        WHERE datname = %s
                    );
                """, (database_name,))
                result = cursor.fetchone()[0]
                cursor.close()
                return result
            else:
                raise ValueError("Unsupported database type for database existence check")
        except ValueError:
            logging.warning(f"Unsupported database type '{self.db_type}' for database creation")
        except Exception as e:
            logging.error(f"Error checking database existence: {e}")
            return False

    # Method to create a database
    def create_database(self, database_name):
        try:
            if self.db_type in ['mysql', 'postgresql']:
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE {database_name};")
                logging.info(f"Database {database_name} created successfully.")
            else:
                raise ValueError("Unsupported database type for database creation")
        except ValueError:
            logging.warning(f"Unsupported database type '{self.db_type}' for database creation")
        except Exception as e:
            logging.error(f"Error creating database {database_name}: {e}")

    # Method to check if a table exists
    def table_exists(self, table_name):
        try:
            cursor = self.connection.cursor()
            if self.db_type == 'postgresql':
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_name = %s
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
                raise ValueError("Unsupported database type for table existence check")
            cursor.close()
            return result
        except ValueError:
            logging.warning(f"Unsupported database type '{self.db_type}' for database creation")
        except Exception as e:
            logging.error(f"Error checking table existence: {e}")
            return False

    # Method to create a table dynamically
    def create_table(self, table_name, columns_definition):
        try:
            if self.db_type == 'mysql':
                if not self.db_config.get('database'):
                    raise ValueError("Database name is not specified in the configuration.")
                cursor = self.connection.cursor()
                cursor.execute(f"USE {self.db_config.get('database')};")  # Select the database
                cursor.close()

            if self.db_type in ['postgresql', 'mysql']:
                query = f"CREATE TABLE {table_name} ({', '.join(columns_definition)})"
            elif self.db_type == 'sqlite':
                query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_definition)})"
            else:
                raise ValueError("Unsupported database type for table creation")

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            logging.info(f"Table {table_name} created successfully.")
        except ValueError:
            logging.warning(f"Unsupported database type '{self.db_type}' for database creation")
        except Exception as e:
            logging.error(f"Error creating table {table_name}: {e}")