
# Program: dbapp.py
# Author: Tom Alexa


import sqlite3
from pathlib import Path

##############
#  contants  #
##############

LANGUAGE = "cz"             # languages → (cz, en)
DB_NAME = "contacts.db"


class App:
    OPTIONS = {
        "q": ("q", "quit", "exit"),
        "l": ("l", "list"),
        "i": ("i", "insert"),
        "d": ("d", "delete")
    }

    def __init__(self, language="cz"):
        self._language = language
        self.load_constants()
        self._db = ContactDatabase()
        self.running = True

    def run(self):
        """
        Main running loop
        """
        while self.running:
            option, parameters = self.get_option()
            self.manage_option(option, parameters)
        self.close()

    def get_option(self):
        """
        Input format: option parameter parameter, ex. l -t contact
        Return: option, parameters (ex. 'l', ['-t', 'contact'])
        """
        self.print_options()
        while True:
            command = list(filter(None, input(self.TO_PRINT["input"][self._language]).strip().split(" ")))
            if not command:
                self.wrong_command()
                continue
            option = command[0].lower()
            parameters = list(map(lambda c: c.strip(), command[1:]))
            if not self.valid_option(option):
                self.wrong_command(option)
                continue
            return option, parameters

    def manage_option(self, option, parameters):
        if option in self.OPTIONS["q"]:
            self.running = False
        elif option in self.OPTIONS["l"]:
            pass
        elif option in self.OPTIONS["i"]:
            pass
        elif option in self.OPTIONS["d"]:
            pass

    def print_options(self):
        print(self.TO_PRINT["print"]["options"][self._language])

    def show(parameters):
        pass

    def insert(parameters):
        pass

    def delete(parameters):
        pass

    def wrong_command(self, option=None):
        print("wrong", option)

    def valid_option(self, option):
        for values in self.OPTIONS.values():
            if option in values: return True
        else: return False

    def load_constants(self):
        dash = "-"
        space = " "
        comma = "."

        dash_options = dash * 80
        spaces_options = space * 6

        self.TO_PRINT = {
            "input": {
                "en": f"{space*4}Choose one option: ",
                "cz": f"{space*4}Vyber jednu z možností: ",
            },
            "print": {
                "options": {
                    "en": f"{dash_options}\nL {comma*20} list all contacts\nL (contact name) ... show contact with given name or similar ones\nL -n (number) ... show contacts with given number or similar\nL -g (group) ... show contacts within group\nL -t (table) ... show all rows in a table\nL -d (date) ... show contacts that date of birth matches with given date → format: YYYY-MM-DD\n{space*78}day: --DD\n{space*76}month: -MM-\n{space*77}year: YYYY--\nI ... insert row into contact table\nI -t (table) ... insert row into table\nD ... delete row from contact table\nD -t (table) ... delete row from table\nQ ... quit the application\n{dash*20}",
                    "cz": f"{spaces_options}{dash_options}\n{spaces_options}| L {comma*16} ukáže všechny kontakty{space*36}|\n{spaces_options}| L (jméno) {comma*8} ukáže kontakt podle jména nebo podobné kontakty{space*11}|\n{spaces_options}| L -n (číslo) {comma*5} ukáže kontakty podle čísla nebo podobné kontakty{space*10}|\n{spaces_options}| L -g (skupina) {comma*3} ukáže kontakty ve skupině{space*33}|\n{spaces_options}| L -t (tabulka) {comma*3} ukáže všechny řádky v tabulce{space*29}|\n{spaces_options}| L -d (datum) {comma*5} ukáže kontakty podle data narození → formát: YYYY-MM-DD{space*3}|\n{spaces_options}|{space*60}den: --DD{space*9}|\n{spaces_options}|{space*58}měsíc: -MM-{space*9}|\n{spaces_options}|{space*60}rok: YYYY--{space*7}|\n{spaces_options}| I {comma*16} vloží kontakt do tabulky{space*34}|\n{spaces_options}| I -t (tabulka) {comma*3} vloží řádek do tabulky{space*36}|\n{spaces_options}| D {comma*16} odstraní kontakt{space*42}|\n{spaces_options}| D -t (tabulka) {comma*3} odstraní řádek z tabulky{space*34}|\n{spaces_options}| Q {comma*16} ukončí aplikaci{space*43}|\n{spaces_options}{dash_options}",
                }
            }
        }

    def close(self):
        self._db.close()


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
                ;
            """,
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
                );
            """,
            """CREATE TABLE IF NOT EXISTS 'prefix' (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefix INTEGER NOT NULL UNIQUE,
                state VARCHAR(255) NOT NULL UNIQUE
                );
            """,
            """CREATE TABLE IF NOT EXISTS 'phone_number' (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefix_id INTEGER NOT NULL DEFAULT 420,
                number INTEGER NOT NULL,
                contact_id INTEGER,
                FOREIGN KEY (prefix_id)
                    REFERENCES prefix(id),
                FOREIGN KEY (contact_id)
                    REFERENCES contact(id)
                );
            """,
        ]
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        for table in tables:
            self.cursor.execute(table)
        self.connection.commit()

    def close(self):
        self.connection.close()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
