import psycopg2
import logging
from psycopg2.extras import execute_values

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class PostgresDB:
    """Класс для работы с базой данных PostgreSQL"""

    def __init__(self, host, user, port, password, db_name):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.db_name = db_name
        self.conn = self.__connect()

    def __connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            conn = psycopg2.connect(
                database=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logging.info("✅ Подключение к PostgreSQL успешно установлено.")
            return conn
        except psycopg2.Error as e:
            logging.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise RuntimeError("Не удалось подключиться к БД")

    def check_connection(self):
        """Проверяет активность соединения и переподключается при необходимости"""
        if self.conn is None or self.conn.closed:
            logging.warning("⚠️ Потеряно соединение с БД, пробуем переподключиться...")
            self.conn = self.__connect()

    def create_table(self, schema):
        """Создает таблицу по схеме (если её нет)"""
        table_name = schema['table_name']
        columns = schema['columns']
        foreign_keys = schema.get('foreign_keys', [])
        unique_constraints = schema.get('constraints', [])

        if self.check_table_exists(table_name):
            logging.warning(f"⚠️ Таблица '{table_name}' уже существует.")
            return

        # Формируем SQL для колонок
        columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])

        # Добавляем PRIMARY KEY, если есть поле 'id'
        if "id" in columns:
            columns_sql = f"id SERIAL PRIMARY KEY, {columns_sql}"

        # Формируем SQL для внешних ключей
        fk_sql = ", ".join([
            f"FOREIGN KEY ({col}) REFERENCES {ref_table}({ref_col})"
            for col, ref_table, ref_col in foreign_keys
        ]) if foreign_keys else ""

        # Формируем SQL для уникальных ограничений
        unique_sql = f", UNIQUE ({', '.join(unique_constraints)})" if unique_constraints else ""

        create_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns_sql}
            {fk_sql if fk_sql else ""}
            {unique_sql}
        );
        """

        try:
            self.check_connection()
            with self.conn as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_query)
                    logging.info(f"✅ Таблица '{table_name}' создана (если её не было).")
        except Exception as e:
            logging.error(f"❌ Ошибка при создании таблицы '{table_name}': {e}")

    def create_indexes(self, table_name, indexes):
        """Создает индексы в таблице"""
        if not indexes:
            logging.warning("⚠️ Нет индексов для создания.")
            return

        try:
            self.check_connection()
            with self.conn as conn:
                with conn.cursor() as cursor:
                    for index in indexes:
                        index_name = f"idx_{index[0]}" if len(index) == 1 else index[1]
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({index[0]});")
                        logging.info(f"✅ Индекс '{index_name}' создан для колонки '{index[0]}' в таблице '{table_name}'.")
        except Exception as e:
            logging.error(f"❌ Ошибка при создании индексов: {e}")

    def check_table_exists(self, table_name):
        """Проверяет, существует ли таблица в базе данных"""
        try:
            self.check_connection()
            with self.conn as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = %s);", (table_name,))
                    return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"❌ Ошибка при проверке таблицы '{table_name}': {e}")
            return False

    def save_to_db(self, table_name, data):
        """Вставляет или обновляет данные в таблице"""
        if not data:
            logging.warning("⚠️ Нет данных для вставки.")
            return

        if not self.check_table_exists(table_name):
            logging.warning(f"⚠️ Таблица '{table_name}' не существует.")
            return

        columns = data[0].keys()
        values = [[row[col] for col in columns] for row in data]

        insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
            {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])};
        """

        try:
            self.check_connection()
            with self.conn as conn:
                with conn.cursor() as cursor:
                    execute_values(cursor, insert_query, values)
                conn.commit()
                logging.info(f"✅ Вставлено/обновлено {len(data)} строк в '{table_name}'.")
        except Exception as e:
            conn.rollback()
            logging.error(f"❌ Ошибка при вставке данных в '{table_name}': {e}")

    def read_from_db(self, table_name, columns=None):
        """Читает данные из таблицы"""
        if not self.check_table_exists(table_name):
            logging.warning(f"⚠️ Таблица '{table_name}' не существует.")
            return []

        columns_sql = ", ".join(columns) if columns else "*"
        query = f"SELECT {columns_sql} FROM {table_name};"

        try:
            self.check_connection()
            with self.conn as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    return rows if rows else []
        except Exception as e:
            logging.error(f"❌ Ошибка при чтении данных из '{table_name}': {e}")
            return []

    def delete_from_db(self, table_name, condition):
        """Удаляет данные из таблицы по условию"""
        if not self.check_table_exists(table_name):
            logging.warning(f"⚠️ Таблица '{table_name}' не существует.")
            return

        query = f"DELETE FROM {table_name} WHERE {condition};"

        try:
            self.check_connection()
            with self.conn as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    conn.commit()
                    logging.info(f"✅ Записи из '{table_name}' удалены по условию: {condition}.")
        except Exception as e:
            conn.rollback()
            logging.error(f"❌ Ошибка при удалении данных из '{table_name}': {e}")

    def close_connection(self):
        """Закрывает соединение с базой"""
        if self.conn:
            self.conn.close()
            logging.info("🔒 Соединение с PostgreSQL закрыто.")
