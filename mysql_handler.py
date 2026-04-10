import os
import logging
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import re

load_dotenv()

class MySQLHandler:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME', 'sis_db')
        self.connection = None

        if not self.password:
            logging.warning("No database password found in .env file!")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logging.info("Successfully connected to MySQL database")
            return True
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("MySQL connection closed")

    def _ensure_connected(self):
        if not self.connection or not self.connection.is_connected():
            return self.connect()
        return True

    def execute_query(self, query, params=None):
        if not self._ensure_connected():
            return []
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logging.error(f"Error executing query: {e}")
            return []

    def execute_update(self, query, params=None):
        if not self._ensure_connected():
            return -1
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected
        except Error as e:
            logging.error(f"Error executing update: {e}")
            self.connection.rollback()
            return -1

    def load_data(self, table_name):
        return self.execute_query(f"SELECT * FROM {table_name}")

    def insert_record(self, table_name, record):
        if not record:
            return False
        columns = list(record.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        return self.execute_update(query, [record[col] for col in columns]) > 0

    def update_record(self, table_name, record, primary_key_field, primary_key_value):
        if not record:
            return 0
        set_clause = ', '.join([f"{col} = %s" for col in record if col != primary_key_field])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key_field} = %s"
        values = [record[col] for col in record if col != primary_key_field] + [primary_key_value]
        return self.execute_update(query, values)

    def delete_record(self, table_name, primary_key_field, primary_key_value):
        query = f"DELETE FROM {table_name} WHERE {primary_key_field} = %s"
        return self.execute_update(query, (primary_key_value,)) > 0

    def validate_student_id(self, student_id):
        return isinstance(student_id, str) and bool(re.match(r'^\d{4}-\d{4}$', student_id))

    def get_total_count(self, table_name, where_clause=None, params=None):
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        result = self.execute_query(query, params)
        return result[0]['count'] if result else 0

    def get_paginated_data(self, table_name, page=1, page_size=10, order_by=None, where_clause=None, params=None):
        offset = (page - 1) * page_size
        query = f"SELECT * FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        if order_by:
            query += f" ORDER BY {order_by}"
        query += f" LIMIT {page_size} OFFSET {offset}"
        return self.execute_query(query, params)

    def record_exists(self, table_name, field, value):
        query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {field} = %s"
        result = self.execute_query(query, (value,))
        return result[0]['count'] > 0 if result else False


COLLEGE_FIELDS = ['code', 'name']
PROGRAM_FIELDS = ['code', 'name', 'college_code']
STUDENT_FIELDS = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']

_shared_db = MySQLHandler()
college_db = _shared_db
program_db = _shared_db
student_db = _shared_db
