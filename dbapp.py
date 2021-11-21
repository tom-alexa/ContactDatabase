
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
    TABLES = {
        "contact": ("contact", "contacts", "c"),
        "phone_number": ("phone_number", "phone_numbers", "number", "numbers", "n"),
        "prefix": ("prefix", "prefixes", "p"),
        "contact_group": ("contact_group", "contact_groups", "group", "groups", "g")
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
        data = {"data": [], "name": "", "subdata": [], "input": "", "chosen": ""}
        valid = True
        done = False
        with_prefix = False
        if parameters:
            mode = None
            for param in parameters:
                if param[0] == "-":
                    param = param.lower()
                    if param in self.PARAMETERS["l"]["table"]:
                        mode = "table"
                    elif param in self.PARAMETERS["l"]["group"]:
                        mode = "group"
                    elif param in self.PARAMETERS["l"]["number"]:
                        mode = "number"
                    elif param in self.PARAMETERS["l"]["date"]:
                        mode = "date"
                    else:
                        valid = False
                        data["name"] = "parameter"
                        data["input"] = param
                        break
                else:
                    if mode == "table":
                        data["input"] = param
                        for table, values in self.TABLES.items():
                            if param in values:
                                break
                        else:
                            valid = False
                            data["name"] = "table"
                            break
                        data["chosen"] = table
                        data["data"], valid, _ = self._db.select(table, {})
                        data["name"] = f"all {table}"
                        break
                    elif mode == "group":
                        data["input"] = param
                        groups, valid, similar_groups = self._db.select("contact_group", {"name": param})
                        if groups:
                            if similar_groups:
                                valid = False
                                data["data"] = groups
                                data["name"] =  "similar group"
                                break
                            data["data"], valid, _ = self._db.select("contact", {"group_id": int(groups[0][0])})
                            data["name"] = "group contact"
                            break
                        else:
                            valid = False
                            data["name"] = "no group"
                            break
                    elif mode == "number":
                        done = True
                        if param[0] == "+":
                            with_prefix = True
                            prefixes, valid, similar = self._db.select("prefix", {"prefix": param[1:]})
                            data["input"] = f"{param} "
                            if similar:
                                data["data"] = prefixes.copy()
                                data["name"] = "similar prefix"
                                break
                            current_numbers, valid, similar = self._db.select("phone_number", {"prefix_id": prefixes[0][0]})
                            data["data"] = current_numbers.copy()
                            data["name"] = "prefix contact"
                            continue
                        data["input"] += param
                        numbers, valid, _ = self._db.select("phone_number", {"number": param}, similar=True)
                        if with_prefix:
                            numbers = list(set(numbers).intersection(current_numbers))
                        if numbers:
                            data["name"] = "number contact"
                            data["subdata"] = numbers.copy()
                            for number in numbers:
                                data["data"], valid, _ = self._db.select("contact", {"id": number[3]})
                            break
                        else:
                            valid = False
                            data["name"] = "no number"
                            break
                    elif mode == "date":
                        data["input"] = param
                        date = param.split("/")
                        if len(date) != 3:
                            valid = False
                            data["name"] = "split date"
                            break
                        elif any(map(lambda x: (x) and (not x.isnumeric()), date)):
                            valid = False
                            data["name"] = "non-numerical date"
                            break
                        data["data"], valid, _ = self._db.select("contact", {"date_of_birth": date})
                        data["name"] = "date contact"
                        break
                    else:
                        rows, valid, similar = self._db.select("contact", {"first_name": param, "last_name": param}, operant="OR")
                        data["data"].extend(rows)
                        if (data["name"] != "name similar contact") and not similar:
                            data["name"] = "name same contact"
                        else:
                            data["name"] = "name similar contact"
                        data["input"] += f"{param} "
                        done = True
            else:
                if not done:
                    valid = False
                    data["name"] = "no parameter"
                    data["input"] = mode
        else:
            data["data"], valid, _ = self._db.select("contact", {})
            for contact in data["data"]:
                groups, valid, _ = self._db.select("contact_group", {"id": contact[4]})
                if groups:
                    data["subdata"].append(groups[0][1])
                else:
                    data["subdata"].append(None)
            data["name"] = "all contact"
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
        space = " "
        dash = "-"

        name = data["name"]
        if name == "all contact":
            print("\n" + self.TO_PRINT["print"]["all contact"][self._language])
            for contact, group in zip(data["data"], data["subdata"]):
                c_id = contact[0]
                first_name = contact[1] if (contact[1] != None) else ""
                last_name = contact[2] if (contact[2] != None) else ""
                date_of_birth = contact[3] if (contact[3] != None) else ""
                group = group if (group != None) else ""
                street = contact[5] if (contact[5] != None) else ""
                number = contact[6] if (contact[6] != None) else ""
                city = contact[7] if (contact[7] != None) else ""

                print(f"{space*6}| {c_id:>6} | {first_name:>12} | {last_name:<12} | {date_of_birth:<10} | {group:<10} | {street:<10} | {number:<6} | {city:<20} |")
        elif name == "no parameter":
            i = data["input"]
            print(self.TO_PRINT["print"]["no parameter"][self._language].replace("*?*", f"'{i}'"))
        print()

    def load_print_constants(self):

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
                },
                "all contact": {
                    "en": f"{space*6}| {space*4}id | {space*7}Jméno | Příjmení{space*4} | Datum nar. | Skupina{space*3} | Ulice{space*5} | ČP.{space*3} | Město{space*15} |",
                    "cz": f"{space*6}| {space*4}id | {space*7}Jméno | Příjmení{space*4} | Datum nar. | Skupina{space*3} | Ulice{space*5} | ČP.{space*3} | Město{space*15} |\n{space*6}{dash*110}",
                },
                "no parameter": {
                    "en": "no parameter",
                    "cz": f"{space*6}Pro *?* chybí parameter"
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

        if table in self.TABLES:
            columns = self.TABLES[table]
        else:
            return "table", False, similar

        where_param = ""
        if parameters:
            add_param = []
            values = []
            for column, value in parameters.items():
                if column not in self.TABLES[table].split(", "):
                    return "column", False, similar
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
