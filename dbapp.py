
# Program: dbapp.py
# Author: Tom Alexa


import sqlite3
import os
from pathlib import Path

##############
#  contants  #
##############

LANGUAGE = "cz"             # languages → (cz, en)
DB_NAME = "contacts.db"


class App:
    def __init__(self):
        self.db = ContactDatabase()

    def run(self):
        pass

    def get_option(self):
        pass

    def manage_option(self, option):
        pass

    def show(parameters):
        pass

    def insert(parameters):
        pass

    def delete(parameters):
        pass


class ContactDatabase:
    def __init__(self):
        self.db_path = Path(f"{Path(__file__).parent.resolve()}/database/{DB_NAME}")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_database()

    def select(self, table, parameters):
        pass

    def create_database(self):
        """
        Create database tables if not already exists
        """
        tables = [
            """CREATE TABLE IF NOT EXISTS 'contact_group' (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE)
                ;""",
            """CREATE TABLE IF NOT EXISTS 'contact' (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name VARCHAR(60),
                last_name VARCHAR(60),
                date_of_birth DATE,
                group_id INTEGER,
                street VARCHAR(60),
                number_of_descriptive INTEGER,
                city VARCHAR(60),
                FOREIGN KEY (group_id)
                    REFERENCES contact_group(id)
                );""",
            """CREATE TABLE IF NOT EXISTS 'prefix' (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefix INTEGER NOT NULL UNIQUE,
                state VARCHAR(255) NOT NULL UNIQUE
                );""",
            """CREATE TABLE IF NOT EXISTS 'phone_number' (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefix_id INTEGER NOT NULL DEFAULT 420,
                number INTEGER NOT NULL, contact_id INTEGER,
                FOREIGN KEY (prefix_id)
                    REFERENCES prefix(id)
                );""",
        ]
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        for table in tables:
            self.cursor.execute(table)
        self.connection.commit()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
