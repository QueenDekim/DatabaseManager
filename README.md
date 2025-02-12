# DatabaseManager class

- A class for managing the connection and performing operations with various types of databases (`SQLite`, `PostgreSQL`, `MySQL`, `REDIS`).
- Supports methods for performing SQL request (`Select`, `Insert`, `Update`, `Delete`) and compound control.

---
## Table of contents / Оглавление
- [Usage Instructions [EN]](#usage-instructions-en)
- [Инструкции по использованию [RU]](#инструкции-по-использованию-ru)
- [Documentation [EN]](#documentation-en)
- [Документация [RU]](#документация-ru)

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

## DatabaseManager Class

### Description
The `DatabaseManager` class is a universal tool for managing connections and performing operations with various types of databases: SQLite, PostgreSQL, MySQL, and Redis. It provides methods for executing basic CRUD (Create, Read, Update, Delete) operations.

---

### Initialization

```python
class DatabaseManager:
    def __init__(self, db_type: str, db_config: dict):
```

#### Parameters:
- **db_type** (`str`): The type of database (`sqlite`, `postgresql`, `mysql`, `redis`).
- **db_config** (`dict`): Configuration for connecting to the database.

---

### Methods

#### 1. `_connect()`
Establishes a connection to the database based on the specified type.

##### Supported Database Types:
- **SQLite**: Uses `sqlite3.connect`.
- **PostgreSQL**: Uses `psycopg2.connect` with autocommit enabled.
- **MySQL**: Uses `pymysql.connect`.
- **Redis**: Uses `redis.Redis`.

##### Exceptions:
- If the database type is unsupported, raises a `ValueError`.

---

#### 2. `execute(method, table, columns='*', data=None, where=None)`
Executes SQL queries for CRUD operations.

##### Parameters:
- **method** (`str`): The operation method (`select`, `insert`, `update`, `delete`).
- **table** (`str`): The name of the table.
- **columns** (`list` or `str`): List of columns or string representation of columns.
- **data** (`list` or `tuple`): Data to insert or update.
- **where** (`str`): The WHERE condition for filtering.

##### Return Value:
- For `select`: Returns the query result (`list`).
- For other methods: Returns `True` if successful, otherwise `False`.

##### Example Usage:
```python
db_manager.execute('insert', 'users', ['name', 'age'], ['Alice', 30])
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 25")
```

---

#### 3. `_execute_redis(method, key, data=None)`
Handles operations with Redis.

##### Parameters:
- **method** (`str`): Operation method (`select`, `insert`, `update`, `delete`).
- **key** (`str`): Key in Redis.
- **data** (`str`): Data to store.

##### Return Value:
- Result of the Redis operation.

##### Example Usage:
```python
db_manager._execute_redis('insert', 'user:1', 'Alice')
result = db_manager._execute_redis('select', 'user:1')
```

---

#### 4. `close()`
Closes the database connection if it exists.

##### Example Usage:
```python
db_manager.close()
```

---

#### 5. `database_exists(database_name)`
Checks if a specific database exists.

##### Parameters:
- **database_name** (`str`): Name of the database.

##### Return Value:
- `True` if the database exists; otherwise, `False`.

##### Example Usage:
```python
if db_manager.database_exists('test_db'):
    print("Database 'test_db' exists.")
else:
    print("Database 'test_db' does not exist.")
```

---

#### 6. `create_database(database_name)`
Creates a new database.

##### Parameters:
- **database_name** (`str`): Name of the new database.

##### Example Usage:
```python
db_manager.create_database('test_db')
```

---

#### 7. `table_exists(table_name)`
Checks if a specific table exists within the current database.

##### Parameters:
- **table_name** (`str`): Name of the table.

##### Return Value:
- `True` if the table exists; otherwise, `False`.

##### Example Usage:
```python
if db_manager.table_exists('users'):
    print("Table 'users' exists.")
else:
    print("Table 'users' does not exist.")
```

---

#### 8. `create_table(table_name, columns_definition)`
Creates a new table with the specified column definitions.

##### Parameters:
- **table_name** (`str`): Name of the new table.
- **columns_definition** (`list`): Definitions for the table's columns.

##### Example Usage:
```python
columns = [
    "id SERIAL PRIMARY KEY",
    "name VARCHAR(100) NOT NULL",
    "age INT"
]
db_manager.create_table('users', columns)
```

---

### Examples of Usage

#### SQLite
```python
from database_manager import DatabaseManager

db_manager = DatabaseManager('sqlite', {'db_name': 'example.db'})
db_manager.execute('insert', 'users', ['name', 'age'], ['Alice', 30])
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 25")
print(result)
```

#### PostgreSQL
```python
from database_manager import DatabaseManager

db_manager = DatabaseManager('postgresql', {
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'database': 'example_db'
})
db_manager.execute('insert', 'users', ['name', 'age'], ['Bob', 25])
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 20")
print(result)
```

#### MySQL
```python
from database_manager import DatabaseManager

db_manager = DatabaseManager('mysql', {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'database': 'example_db'
})
db_manager.execute('insert', 'users', ['name', 'age'], ['Charlie', 22])
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 20")
print(result)
```

#### Redis
```python
from database_manager import DatabaseManager

db_manager = DatabaseManager('redis', {'host': 'localhost', 'port': 6379})
db_manager.execute('insert', 'user:1', 'Alice')
result = db_manager.execute('select', 'user:1')
print(result)
```

---

# Документация [RU]

## DatabaseManager Class

### Описание
Класс `DatabaseManager` представляет собой универсальный инструмент для управления подключением и выполнения операций с различными типами баз данных: SQLite, PostgreSQL, MySQL и Redis. Он предоставляет методы для выполнения основных операций CRUD (Create, Read, Update, Delete).

---

### Инициализация класса

```python
class DatabaseManager:
    def __init__(self, db_type: str, db_config: dict):
```

#### Параметры:
- **db_type** (`str`): Тип базы данных (`sqlite`, `postgresql`, `mysql`, `redis`).
- **db_config** (`dict`): Конфигурация подключения к базе данных. Структура зависит от типа базы данных.

---

### Методы класса

#### 1. `_connect()`
Устанавливает соединение с базой данных в зависимости от указанного типа.

##### Реализация:
```python
def _connect(self):
```

##### Поддерживаемые типы баз данных:
- **SQLite**: Использует `sqlite3.connect`.
- **PostgreSQL**: Использует `psycopg2.connect` с включенным автокоммитом.
- **MySQL**: Использует `pymysql.connect`.
- **Redis**: Использует `redis.Redis`.

##### Исключения:
- Если тип базы данных не поддерживается, вызывается `ValueError`.

---

#### 2. `execute(method, table, columns='*', data=None, where=None)`
Выполняет SQL-запросы для операций CRUD.

##### Параметры:
- **method** (`str`): Метод запроса (`select`, `insert`, `update`, `delete`).
- **table** (`str`): Название таблицы.
- **columns** (`list` или `str`): Список столбцов или строковое представление столбцов.
- **data** (`list` или `tuple`): Данные для записи (для `insert` и `update`).
- **where** (`str`): Условие фильтрации (для `update` и `delete`).

##### Возвращаемое значение:
- Для `select`: Возвращает результат выборки (`list`).
- Для остальных методов: Возвращает `True` при успешном выполнении или `False` при ошибке.

##### Пример использования:
```python
db_manager.execute('insert', 'users', ['name', 'age'], ['Alice', 30])
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 25")
```

---

#### 3. `_execute_redis(method, key, data=None)`
Выполняет операции с Redis.

##### Параметры:
- **method** (`str`): Метод операции (`select`, `insert`, `update`, `delete`).
- **key** (`str`): Ключ в Redis.
- **data** (`str`): Данные для записи.

##### Возвращаемое значение:
- Результат выполнения операции.

##### Пример использования:
```python
db_manager._execute_redis('insert', 'user:1', 'Alice')
result = db_manager._execute_redis('select', 'user:1')
```

---

#### 4. `close()`
Закрывает соединение с базой данных, если оно существует.

##### Пример использования:
```python
db_manager.close()
```

---

#### 5. `database_exists(database_name)`
Проверяет существование указанной базы данных.

##### Параметры:
- **database_name** (`str`): Название базы данных.

##### Возвращаемое значение:
- `True`, если база данных существует; иначе `False`.

##### Пример использования:
```python
if db_manager.database_exists('test_db'):
    print("База данных 'test_db' существует.")
else:
    print("База данных 'test_db' не существует.")
```

---

#### 6. `create_database(database_name)`
Создает новую базу данных.

##### Параметры:
- **database_name** (`str`): Название новой базы данных.

##### Пример использования:
```python
db_manager.create_database('test_db')
```

---

#### 7. `table_exists(table_name)`
Проверяет существование указанной таблицы.

##### Параметры:
- **table_name** (`str`): Название таблицы.

##### Возвращаемое значение:
- `True`, если таблица существует; иначе `False`.

##### Пример использования:
```python
if db_manager.table_exists('users'):
    print("Таблица 'users' существует.")
else:
    print("Таблица 'users' не существует.")
```

---

#### 8. `create_table(table_name, columns_definition)`
Создает новую таблицу.

##### Параметры:
- **table_name** (`str`): Название таблицы.
- **columns_definition** (`list`): Определение столбцов таблицы.

##### Пример использования:
```python
columns = [
    "id SERIAL PRIMARY KEY",
    "name VARCHAR(100) NOT NULL",
    "age INT"
]
db_manager.create_table('users', columns)
```

---

### Примеры использования

#### SQLite
```python
from database_manager import DatabaseManager

db_manager = DatabaseManager('sqlite', {'db_name': 'example.db'})
db_manager.execute('insert', 'users', ['name', 'age'], ['Alice', 30])
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 25")
print(result)
```

#### PostgreSQL
```python
from database_manager import DatabaseManager

db_manager = DatabaseManager('postgresql', {
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'database': 'example_db'
})
db_manager.execute('insert', 'users', ['name', 'age'], ['Bob', 25])
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 20")
print(result)
```

#### MySQL
```python
from database_manager import DatabaseManager

db_manager = DatabaseManager('mysql', {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'database': 'example_db'
})
db_manager.execute('insert', 'users', ['name', 'age'], ['Charlie', 22])
result = db_manager.execute('select', 'users', ['name', 'age'], where="age > 20")
print(result)
```

#### Redis
```python
from database_manager import DatabaseManager

db_manager = DatabaseManager('redis', {'host': 'localhost', 'port': 6379})
db_manager.execute('insert', 'user:1', 'Alice')
result = db_manager.execute('select', 'user:1')
print(result)
```