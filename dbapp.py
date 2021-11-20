
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

    def create_database(self):
        pass

    def select(self, table, parameters):
        pass


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
