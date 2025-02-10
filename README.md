# DatabaseManager class

- A class for managing the connection and performing operations with various types of databases (`SQLite`, `PostgreSQL`, `MySQL`, `REDIS`).
- Supports methods for performing SQL request (`Select`, `Insert`, `Update`, `Delete`) and compound control.

---

# Usage Instructions [EN]

1. Install required libraries:
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt

   # Linux
   python3 -m venv .venv
   . ./.venv/bin/activate # or 'source ./.venv/bin/activate'
   pip3 install -r requirements.txt
   ```

2. Import the class in your Python script:

    ```py
    from database_manager import DatabaseManager
    ```

---

# Инструкции по использованию [RU]

1. Установите необходимые библиотеки:
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt

   # Linux
   python3 -m venv .venv
   . ./.venv/bin/activate # или 'source ./.venv/bin/activate'
   pip3 install -r requirements.txt
   ```

2. Импортируйте класс в свой скрипт Python:

    ```py
    from database_manager import DatabaseManager
    ```


# Documentation [EN]

## Class `DatabaseManager`

The `DatabaseManager` class is a universal manager for working with various types of databases: SQLite, PostgreSQL, MySQL, and Redis. It provides methods for performing basic CRUD (Create, Read, Update, Delete) operations.

### Class Initialization

```python
class DatabaseManager:
    def __init__(self, db_type, db_config):
        self.db_type = db_type.lower()
        self.db_config = db_config
        try:
            self.connection = self._connect()
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            self.connection = None
```
#### Parameters:

- `db_type`: The type of database (`sqlite`, `postgresql`, `mysql`, `redis`).
- `db_config`: Connection configuration for the database.

---

### Methods of the `DatabaseManager` Class

#### 1. `_connect()`

This method establishes a connection to the database depending on the type.
```python
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
        logging.warning(f"Unsupported database type '{self.db_type}'")
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
```

---

#### 2. `execute(method, table, columns='*', data=None, where=None)`

This method executes SQL queries for CRUD operations.
```python
def execute(self, method, table, columns='*', data=None, where=None):
    try:
        if self.db_type == 'redis':
            return self._execute_redis(method, table, data)
        cursor = self.connection.cursor()
        query = ""

        if self.db_type == 'mysql':
            if self.db_config.get('database'):
                cursor.execute(f"USE {self.db_config.get('database')};")

        if self.db_type == 'sqlite':
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
                placeholders = ', '.join(['?'] * len(data))
                query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(query, tuple(data))
            elif method.lower() == 'update':
                set_clause = ', '.join([f"{col} = ?" for col in columns])
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
```

---

#### 3. `_execute_redis(method, key, data=None)`

This method handles operations with Redis.
```python
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
```

#### 4. `close`

Closes the database connection if it exists.

```py
def close(self):
    try:
        if self.db_type in ['sqlite', 'postgresql', 'mysql'] and self.connection:
            self.connection.close()
    except Exception as e:
        logging.error(f"Error closing database connection: {e}")
```

#### 5. `database_exists(database_name)`

Checks if a specific database exists.

```py
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
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            result = cursor.fetchone() is not None
            cursor.close()
            return result
        else:
            raise ValueError("Unsupported database type for database existence check")
    except ValueError:
        logging.warning(f"Unsupported database type '{self.db_type}' for database existence check")
    except Exception as e:
        logging.error(f"Error checking database existence: {e}")
        return False
```

#### 6. `create_database(database_name)`

Creates a new database.

```py
def create_database(self, database_name):
    try:
        if self.db_type == 'mysql':
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE {database_name};")
            logging.info(f"Database {database_name} created successfully.")
        elif self.db_type == 'postgresql':
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE {database_name};")
            self.connection.commit()
            logging.info(f"Database {database_name} created successfully.")
            # необходимо переключиться на созданную базу данных
            self.db_config['database'] = database_name
            self.connection.close()
            self.connection = self._connect()
        else:
            raise ValueError("Unsupported database type for database creation")
    except ValueError:
        logging.warning(f"Unsupported database type '{self.db_type}' for database creation")
    except Exception as e:
        logging.error(f"Error creating database {database_name}: {e}")
```

#### 7. `table_exists(table_name)`

Checks if a specific table exists within the current database.

```py
def table_exists(self, table_name):
    try:
        cursor = self.connection.cursor()
        if self.db_type == 'postgresql':
            cursor = self.connection.cursor()
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
            raise ValueError("Unsupported database type for table existence check")
        cursor.close()
        return result
    except ValueError:
        logging.warning(f"Unsupported database type '{self.db_type}' for table existence check")
    except Exception as e:
        logging.error(f"Error checking table existence: {e}")
        return False
```

#### 8. `create_table(table_name, columns_definition)`

Creates a new table with the specified column definitions.

```py
def create_table(self, table_name, columns_definition):
    try:
        if self.db_type == 'mysql':
            if not self.db_config.get('database'):
                raise ValueError("Database name is not specified in the configuration.")
            cursor = self.connection.cursor()
            cursor.execute(f"USE {self.db_config.get('database')};")  # Select the database
            cursor.close()
        if self.db_type == 'postgresql':
            cursor = self.connection.cursor()
            query = f"CREATE TABLE {table_name} ({', '.join(columns_definition)})"
            cursor.execute(query)
            self.connection.commit()
            logging.info(f"Table {table_name} created successfully.")
        if self.db_type in ['sqlite', 'mysql']:
            if self.db_type == 'sqlite':
                query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_definition)})"
            else:
                query = f"CREATE TABLE {table_name} ({', '.join(columns_definition)})"
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            logging.info(f"Table {table_name} created successfully.")
        elif self.db_type == 'redis':
            logging.info(f"Table {table_name} created successfully.")
    except Exception as e:
        logging.error(f"Error creating table {table_name}: {e}")
```

---

### Examples of Using `DatabaseManager`

#### SQLite

```python
from database_manager import DatabaseManager
# Initialization
db_manager = DatabaseManager('sqlite', {'db_name': 'example.db'})
# Inserting data
db_manager.execute('insert', 'users', ['name', 'age'], ['Alice', 30])
# Retrieving data
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 25")
print(result)
# Updating data
db_manager.execute('update', 'users', ['age'], [35], where="name = 'Alice'")
# Deleting data
db_manager.execute('delete', 'users', where="name = 'Alice'")
```
---

#### PostgreSQL

```python
from database_manager import DatabaseManager
# Initialization
db_manager = DatabaseManager('postgresql', {
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'database': 'example_db'
})
# Inserting data
db_manager.execute('insert', 'users', ['name', 'age'], ['Bob', 25])
# Retrieving data
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 20")
print(result)
# Updating data
db_manager.execute('update', 'users', ['age'], [30], where="name = 'Bob'")
# Deleting data
db_manager.execute('delete', 'users', where="name = 'Bob'")
```
---

#### MySQL

```python
from database_manager import DatabaseManager
# Initialization
db_manager = DatabaseManager('mysql', {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'database': 'example_db'
})
# Inserting data
db_manager.execute('insert', 'users', ['name', 'age'], ['Charlie', 22])
# Retrieving data
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 20")
print(result)
# Updating data
db_manager.execute('update', 'users', ['age'], [25], where="name = 'Charlie'")
# Deleting data
db_manager.execute('delete', 'users', where="name = 'Charlie'")
```
---

#### Redis

```python
from database_manager import DatabaseManager
# Initialization
db_manager = DatabaseManager('redis', {'host': 'localhost', 'port': 6379})
# Inserting data
db_manager.execute('insert', 'user:1', 'Alice')
# Retrieving data
result = db_manager.execute('select', 'user:1')
print(result)
# Updating data
db_manager.execute('update', 'user:1', 'Bob')
# Deleting data
db_manager.execute('delete', 'user:1')
```

#### Example of `database_exists`

```python
from database_manager import DatabaseManager

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost'
}

db_manager = DatabaseManager('mysql', db_config)

# Check if a database exists
if db_manager.database_exists('test_db'):
    print("Database 'test_db' exists.")
else:
    print("Database 'test_db' does not exist.")
```

#### Example of `create_database`

```python
from database_manager import DatabaseManager

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost'
}

db_manager = DatabaseManager('mysql', db_config)

db_manager.create_database('test_db')
print("Database 'test_db' has been created.")
```

#### Example of `table_exists`

```python
from database_manager import DatabaseManager

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost'
}

db_manager = DatabaseManager('mysql', db_config)

# Assuming we are connected to 'test_db'
if db_manager.table_exists('users'):
    print("Table 'users' exists.")
else:
    print("Table 'users' does not exist.")
```

#### Example of `create_table`

```python
from database_manager import DatabaseManager

# Define column definitions
columns = [
    "id SERIAL PRIMARY KEY",
    "name VARCHAR(100) NOT NULL",
    "age INT"
]

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost'
}

db_manager = DatabaseManager('mysql', db_config)

# Create a new table
db_manager.create_table('users', columns)
print("Table 'users' has been created.")
```

---

# Документация [RU]

## Класс `DatabaseManager`

Класс `DatabaseManager` является универсальным менеджером для работы с различными типами баз данных: SQLite, PostgreSQL, MySQL и Redis. Он предоставляет методы для выполнения основных операций CRUD (Create, Read, Update, Delete).

### Инициализация класса

```python
class DatabaseManager:
    def __init__(self, db_type, db_config):
        self.db_type = db_type.lower()
        self.db_config = db_config
        try:
            self.connection = self._connect()
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            self.connection = None
```

#### Параметры:
- `db_type`: Тип базы данных (`sqlite`, `postgresql`, `mysql`, `redis`).
- `db_config`: Конфигурация подключения к базе данных.

---

### Методы класса `DatabaseManager`

#### 1. `_connect()`
Метод устанавливает соединение с базой данных в зависимости от типа.

```python
def _connect(self):
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
            raise ValueError("Unsupported database type")
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
```

---

#### 2. `execute(method, table, columns='*', data=None, where=None)`
Метод выполняет SQL-запросы для операций CRUD.

```python
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
```

---

#### 3. `_execute_redis(method, key, data=None)`
Метод для работы с Redis.

```python
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
```


#### 4. `close`
Закрывает соединение базы данных, если оно существует.

```py
def close(self):
    try:
        if self.db_type in ['sqlite', 'postgresql', 'mysql'] and self.connection:
            self.connection.close()
    except Exception as e:
        logging.error(f"Error closing database connection: {e}")
```

#### 5. `database_exists(database_name)`
Проверяет, существует ли конкретная база данных.

```py
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
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            result = cursor.fetchone() is not None
            cursor.close()
            return result
        else:
            raise ValueError("Unsupported database type for database existence check")
    except ValueError:
        logging.warning(f"Unsupported database type '{self.db_type}' for database existence check")
    except Exception as e:
        logging.error(f"Error checking database existence: {e}")
        return False
```

#### 6. `create_database(database_name)`
Создает новую базу данных.

```py
def create_database(self, database_name):
    try:
        if self.db_type == 'mysql':
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE {database_name};")
            logging.info(f"Database {database_name} created successfully.")
        elif self.db_type == 'postgresql':
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE {database_name};")
            self.connection.commit()
            logging.info(f"Database {database_name} created successfully.")
            # необходимо переключиться на созданную базу данных
            self.db_config['database'] = database_name
            self.connection.close()
            self.connection = self._connect()
        else:
            raise ValueError("Unsupported database type for database creation")
    except ValueError:
        logging.warning(f"Unsupported database type '{self.db_type}' for database creation")
    except Exception as e:
        logging.error(f"Error creating database {database_name}: {e}")
```

#### 7. `table_exists(table_name)`
Проверяет, существует ли конкретная таблица в текущей базе данных.

```py
def table_exists(self, table_name):
    try:
        cursor = self.connection.cursor()
        if self.db_type == 'postgresql':
            cursor = self.connection.cursor()
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
            raise ValueError("Unsupported database type for table existence check")
        cursor.close()
        return result
    except ValueError:
        logging.warning(f"Unsupported database type '{self.db_type}' for table existence check")
    except Exception as e:
        logging.error(f"Error checking table existence: {e}")
        return False
```

#### 8. `create_table(table_name, columns_definition)`
Создает новую таблицу с указанными определениями столбцов.

```py
def create_table(self, table_name, columns_definition):
    try:
        if self.db_type == 'mysql':
            if not self.db_config.get('database'):
                raise ValueError("Database name is not specified in the configuration.")
            cursor = self.connection.cursor()
            cursor.execute(f"USE {self.db_config.get('database')};")  # Select the database
            cursor.close()
        if self.db_type == 'postgresql':
            cursor = self.connection.cursor()
            query = f"CREATE TABLE {table_name} ({', '.join(columns_definition)})"
            cursor.execute(query)
            self.connection.commit()
            logging.info(f"Table {table_name} created successfully.")
        if self.db_type in ['sqlite', 'mysql']:
            if self.db_type == 'sqlite':
                query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_definition)})"
            else:
                query = f"CREATE TABLE {table_name} ({', '.join(columns_definition)})"
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            logging.info(f"Table {table_name} created successfully.")
        elif self.db_type == 'redis':
            logging.info(f"Table {table_name} created successfully.")
    except Exception as e:
        logging.error(f"Error creating table {table_name}: {e}")
```


---

### Примеры использования `DatabaseManager`

#### SQLite

```python
from database_manager import DatabaseManager

# Инициализация
db_manager = DatabaseManager('sqlite', {'db_name': 'example.db'})

# Вставка данных
db_manager.execute('insert', 'users', ['name', 'age'], ['Alice', 30])

# Выборка данных
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 25")
print(result)

# Обновление данных
db_manager.execute('update', 'users', ['age'], [35], where="name = 'Alice'")

# Удаление данных
db_manager.execute('delete', 'users', where="name = 'Alice'")
```

---

#### PostgreSQL

```python
from database_manager import DatabaseManager

# Инициализация
db_manager = DatabaseManager('postgresql', {
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'database': 'example_db'
})

# Вставка данных
db_manager.execute('insert', 'users', ['name', 'age'], ['Bob', 25])

# Выборка данных
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 20")
print(result)

# Обновление данных
db_manager.execute('update', 'users', ['age'], [30], where="name = 'Bob'")

# Удаление данных
db_manager.execute('delete', 'users', where="name = 'Bob'")
```

---

#### MySQL

```python
from database_manager import DatabaseManager

# Инициализация
db_manager = DatabaseManager('mysql', {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'database': 'example_db'
})

# Вставка данных
db_manager.execute('insert', 'users', ['name', 'age'], ['Charlie', 22])

# Выборка данных
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 20")
print(result)

# Обновление данных
db_manager.execute('update', 'users', ['age'], [25], where="name = 'Charlie'")

# Удаление данных
db_manager.execute('delete', 'users', where="name = 'Charlie'")
```

---

#### Redis

```python
from database_manager import DatabaseManager

# Инициализация
db_manager = DatabaseManager('redis', {'host': 'localhost', 'port': 6379})

# Вставка данных
db_manager.execute('insert', 'user:1', 'Alice')

# Выборка данных
result = db_manager.execute('select', 'user:1')
print(result)

# Обновление данных
db_manager.execute('update', 'user:1', 'Bob')

# Удаление данных
db_manager.execute('delete', 'user:1')
```

#### Пример `database_exists`

```python
from database_manager import DatabaseManager

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost'
}

db_manager = DatabaseManager('mysql', db_config)

# Check if a database exists
if db_manager.database_exists('test_db'):
    print("База данных 'test_db' существует.")
else:
    print("База данных 'test_db' не существует.")
```

#### Пример `create_database`

```python
from database_manager import DatabaseManager

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost'
}

db_manager = DatabaseManager('mysql', db_config)

db_manager.create_database('test_db')
print("База данных 'test_db' была создана.")
```

#### Пример `table_exists`

```python
from database_manager import DatabaseManager

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost'
}

db_manager = DatabaseManager('mysql', db_config)

if db_manager.table_exists('users'):
    print("Таблица 'users' существуют.")
else:
    print("Таблица 'users' не существует.")
```

#### Пример `create_table`

```python
from database_manager import DatabaseManager

# Определить определения столбцов
columns = [
    "id SERIAL PRIMARY KEY",
    "name VARCHAR(100) NOT NULL",
    "age INT"
]

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost'
}

db_manager = DatabaseManager('mysql', db_config)

# Создать новую таблицу
db_manager.create_table('users', columns)
print("Таблица 'users' были созданы.")
```