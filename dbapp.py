
# Program: dbapp.py
# Author: Tom Alexa


import sqlite3
from pathlib import Path

##############
#  contants  #
##############

# languages → (cz, en)
LANGUAGE = "cz"
DB_NAME = "contacts.db"


#############
#  classes  #
#############

class App:
    OPTIONS = {
        "q": ("q", "quit", "exit"),
        "l": ("l", "list"),
        "i": ("i", "insert"),
        "d": ("d", "delete"),
        "h": ("h", "help")
    }
    PARAMETERS = {
        "l": {
            "table": ("-t", "--table"),
            "group": ("-g", "--group"),
            "number": ("-n", "--number"),
            "date": ("-d", "--date"),
        }
    }

    def __init__(self, language):
        self._language = language
        self.load_print_constants()
        self._db = ContactDatabase()
        self.running = True

    def run(self):
        """
        Main running loop
        """
        self.print_options()
        while self.running:
            option, parameters = self.get_option()
            self.manage_option(option, parameters)
        self.close()

    def get_option(self):
        """
        Input format: option parameter parameter, ex. l -t contact
        Return: option, parameters (ex. 'l', ['-t', 'contact'])
        """
        while True:
            command = list(filter(None, input(self.TO_PRINT["input"][self._language]).strip().split(" ")))
            if not command:
                continue
            option = command[0].lower()
            parameters = list(map(lambda c: c.strip(), command[1:]))
            if not self.valid_option(option):
                self.wrong_command(option)
                continue
            return option, parameters

    def manage_option(self, option, parameters):
        if option in self.OPTIONS["q"]:     # quit
            self.running = False
        elif option in self.OPTIONS["h"]:   # help
            self.print_options()
        elif option in self.OPTIONS["l"]:   # list
            self.show(parameters)
        elif option in self.OPTIONS["i"]:   # insert
            pass
        elif option in self.OPTIONS["d"]:   # delete
            pass

    def show(self, parameters):
        data = {"data": [], "table": None, "mode": None, "subdata": []}
        valid = True
        if parameters:
            mode = None
            for param in parameters:
                if param[0] == "-":
                    param = param.lower()
                    if param in self.PARAMETERS["l"]["table"]:
                        mode = "table"
                        data["mode"] = "table"
                    elif param in self.PARAMETERS["l"]["group"]:
                        mode = "group"
                        data["mode"] = "group"
                    elif param in self.PARAMETERS["l"]["number"]:
                        mode = "number"
                        data["mode"] = "number"
                    elif param in self.PARAMETERS["l"]["date"]:
                        mode = "date"
                        data["mode"] = "date"
                    else:
                        valid = False
                        data["data"] = ["parameter"]
                        data["subdata"].append(param)
                        break
                else:
                    if mode == "table":
                        data["data"], valid, _ = self._db.select(param, {})
                        data["table"] = param
                        data["mode"] = "all"
                    elif mode == "group":
                        groups, valid = self._db.select("group", {"name": param})
                        if groups:
                            data["data"], valid = self._db.select("contact", {"group_id": int(data[0][0])})
                            data["table"] = "contact"
                            data["mode"] = "group"
                            data["subdata"].extend(param)
                        else:
                            data["data"], valid = ["group"], False
                    elif mode == "number":
                        numbers, valid, similar = self._db.select("phone_number", {"number": param})
                        if numbers:
                            for number in numbers:
                                rows, valid = self._db.select("contact", {"id": number[0]})
                                data["data"].extend(rows)
                                data["subdata"].append(number)
                                data["table"] = "contact"
                                data["mode"] = "number"
                        else:
                            valid = False
                            data["data"] = ["number"]
                            data["subdata"].append(param)
                    elif mode == "date":
                        date = param.split("/")
                        if len(date) != 3:
                            valid = False
                        elif any(map(lambda x: (x) and (not x.isnumeric()), date)):
                            valid = False
                        if not valid:
                            data["data"] = ["date"]
                            break
                        data["data"], valid, _ = self._db.select("contact", {"date_of_birth": date})
                        data["table"] = "contact"
                        data["mode"] = "date"
                    else:
                        rows, valid, similar = self._db.select("contact", {"first_name": param, "last_name": param}, operant="OR")
                        data["data"].extend(rows)
                        data["table"] = "contact"
                        data["mode"] = "name same"
                        if similar:
                            data["mode"] = "name similar"
                        data["subdata"].append(param)
        else:
            data["data"], valid, _ = self._db.select(self.DEFAULT_TABLE, {})
            data["table"] = "contact"
            data["mode"] = "all"
        self.print_show(data, valid)

    def insert(parameters):
        pass

    def delete(parameters):
        pass

    def wrong_command(self, option):
        print(self.TO_PRINT["print"]["wrong"][self._language].replace("*?*", f"'{option}'"))

    def valid_option(self, option):
        for values in self.OPTIONS.values():
            if option in values: return True
        else: return False

    def print_options(self):
        print(self.TO_PRINT["print"]["options"][self._language])

    def print_show(self, data, valid):
        print(data, valid)

    def load_print_constants(self):
        self.DEFAULT_TABLE = "contact"

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
                    "en": f"{dash_options}\nH {comma*20} show this table\nL {comma*20} list all contacts\nL (contact name) ... show contact with given name or similar ones\nL -n (number) ... show contacts with given number or similar\nL -g (group) ... show contacts within group\nL -t (table) ... show all rows in a table\nL -d (date) ... show contacts that date of birth matches with given date → format: YYYY-MM-DD\n{space*78}day: --DD\n{space*76}month: -MM-\n{space*77}year: YYYY--\nI ... insert row into contact table\nI -t (table) ... insert row into table\nD ... delete row from contact table\nD -t (table) ... delete row from table\nQ ... quit the application\n{dash*20}",
                    "cz": f"{spaces_options}{dash_options}\n{spaces_options}| H {comma*16} ukáže tuto tabulku{space*40}|\n{spaces_options}| L (jméno) {comma*8} ukáže kontakt podle jména nebo podobné kontakty{space*11}|\n{spaces_options}| L -n (číslo) {comma*5} ukáže kontakty podle čísla nebo podobné kontakty{space*10}|\n{spaces_options}| L -g (skupina) {comma*3} ukáže kontakty ve skupině{space*33}|\n{spaces_options}| L -t (tabulka) {comma*3} ukáže všechny řádky v tabulce{space*29}|\n{spaces_options}| L -d (datum) {comma*5} ukáže kontakty podle data narození → formát: YYYY/MM/DD{space*3}|\n{spaces_options}|{space*60}den: //DD{space*9}|\n{spaces_options}|{space*58}měsíc: /MM/{space*9}|\n{spaces_options}|{space*60}rok: YYYY//{space*7}|\n{spaces_options}| I {comma*16} vloží kontakt do tabulky{space*34}|\n{spaces_options}| I -t (tabulka) {comma*3} vloží řádek do tabulky{space*36}|\n{spaces_options}| D {comma*16} odstraní kontakt{space*42}|\n{spaces_options}| D -t (tabulka) {comma*3} odstraní řádek z tabulky{space*34}|\n{spaces_options}| Q {comma*16} ukončí aplikaci{space*43}|\n{spaces_options}{dash_options}",
                },
                "wrong": {
                    "en": f"{space*6}Bash *?* does not exists!\n",
                    "cz": f"{space*6}Příkaz *?* neexistuje!\n",
                }
            }
        }

    def close(self):
        self._db.close()


class ContactDatabase:
    TABLES = {
        "contact": "id, first_name, last_name, date_of_birth, group_id, street, number_of_descriptive, city",
        "contact_group": "id, name",
        "prefix": "id, prefix, state",
        "phone_number": "id, prefix_id, number, contact_id"
    }

    def __init__(self):
        self.db_path = Path(f"{Path(__file__).parent.resolve()}/database/{DB_NAME}")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_database()

    def select(self, table, parameters: dict, operant="AND", similar=False):
        if table == "group":
            table = "contact_group"
        if table in self.TABLES:
            columns = self.TABLES[table]
        else:
            return ["table"], False, similar

        where_param = ""
        if parameters:
            add_param = []
            values = []
            for column, value in parameters.items():
                if column not in self.TABLES[table].split(", "):
                    return ["column"], False, similar
                if column == "date_of_birth":
                    add_param.append(r"strftime('%Y', date_of_birth) = ? OR strftime('%m', date_of_birth) = ? OR strftime('%d', date_of_birth) = ?")
                    year = value[0]
                    month = value[1]
                    day = value[2]
                    if year:
                        values.append(f"{int(year):04d}")
                    else:
                        values.append(year)
                    if month:
                        values.append(f"{int(month):02d}")
                    else:
                        values.append(month)
                    if day:
                        values.append(f"{int(day):02d}")
                    else:
                        values.append(day)
                    continue
                if similar:
                    add_param.append(f"{column} LIKE ?")
                else:
                    add_param.append(f"{column} = ?")
                values.append(value)
            where_param += " WHERE " + f" {operant} ".join(add_param)

        if parameters:
            if similar:
                self.cursor.execute(f"SELECT {columns} FROM {table}{where_param};", tuple(map(lambda v: f"%{v}%", values)))
            else:
                self.cursor.execute(f"SELECT {columns} FROM {table}{where_param};", tuple(values))
        else:
            self.cursor.execute(f"SELECT {columns} FROM {table};")

        data = self.cursor.fetchall()
        if data or similar: return data, True, similar
        return self.select(table, parameters, operant, similar=True)

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
        self.cursor.execute("PRAGMA case_sensitive_like = false;")
        for table in tables:
            self.cursor.execute(table)
        self.connection.commit()

    def close(self):
        self.connection.close()


#################
#  main script  #
#################

def main():
    app = App(LANGUAGE)
    app.run()


if __name__ == "__main__":
    main()
