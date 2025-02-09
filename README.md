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

This method executes SQL queries for CRUD operations.
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