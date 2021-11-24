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

    ##########
    #  main  #
    ##########

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

    ##########
    #  show  #
    ##########

    def show(self, parameters):
        data = {"data": [], "name": "", "input": "", "chosen": "", "valid": True}
        if parameters:
            mode = None
            for param in parameters:
                if param[0] == "-":
                    mode = self.get_parameter_mode(data, param)
                    if not self.check_valid_param(data, param, "parameter"):
                        break

                else:
                    if mode == "table":
                        self.mode_table(data, param)
                        self.check_valid_param(data, param, "table")
                        break

                    elif mode == "group":
                        self.mode_group(data, param)
                        self.check_valid_param(data, param)
                        break

                    elif mode == "number":
                        done = self.mode_number(data, param)
                        self.check_valid_param(data, param)
                        if done: break

                    elif mode == "date":
                        self.mode_data(data, param)


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
                if not data["input"]:
                    data["name"] = f"no parameter {mode}"
        else:
            self.mode_table(data, "contact")
        print(data)
        self.print_show(data)

    #########################
    #  show → subfunctions  #
    #########################

    def valid_option(self, option):
        for values in self.OPTIONS.values():
            if option in values: return True
        else: return False

    def get_parameter_mode(self, data, param):
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
            mode = None
            data["valid"] = False
        return mode

    def check_valid_param(self, data, param, error_name=None):
        if not data["valid"]:
            data["input"] = param
            if error_name:
                data["name"] = error_name
            return False
        return True

    ##################
    #  show → modes  #
    ##################

    def mode_table(self, data, table_name):
        data["input"] = table_name
        for table, values in self.TABLES.items():
            if table_name in values:
                break
        else:
            data["valid"] = False
            data["name"] = "table"
            return
        data["chosen"] = table
        data["data"], _, _ = self._db.select(table, {})
        data["name"] = f"all {table}"

        if table == "contact":
            self.change_to_group(data)
        elif table == "phone_number":
            self.add_plus_sign(data)
        elif table == "prefix":
            self.add_plus_sign(data)

    def mode_group(self, data, group_name):
        groups, _, similar_groups = self._db.select("contact_group", {"name": group_name})
        if not groups:
            data["valid"] = False
            data["name"] = "no group"
            return
        if similar_groups:
            data["valid"] = False
            data["data"] = groups
            data["name"] =  "similar group"
            return
        data["chosen"] = groups[0][1]
        data["data"], _, _ = self._db.select("contact", {"group_id": int(groups[0][0])})
        data["name"] = "group contact"

    def mode_number(self, data, param):
        if not (param.isnumeric() and int(param) > 0):
            if (param[0] != "+") or (not param[1:].isnumeric()):
                data["valid"] = False
                data["name"] = "not number"
                return True

        if param[0] == "+":
            prefixes, _, similar = self._db.select("prefix", {"prefix": param[1:]})
            data["input"] = param
            if similar:
                data["valid"] = False
                data["data"] = prefixes
                data["name"] = "similar prefix"
                return True

            data["data"], _, _ = self._db.select("phone_number", {"prefix_id": prefixes[0][0]})
            data["name"] = "prefix contact"
            return False

        if data["input"]:
            data["input"] += f"{param} "
            numbers, _, _ = self._db.select("phone_number", {"number": param, "prefix_id": data["input"][1:]}, similar=True)
        else:
            numbers, _, _ = self._db.select("phone_number", {"number": param}, similar=True)
            data["input"] = param

        if not numbers:
            data["valid"] = False
            data["name"] = "no number"
            return True

        data["name"] = "number contact"
        active_ids = set()
        data["data"] = {}
        for number in numbers:
            rows, _, _ = self._db.select("contact", {"id": number[3]})
            contact_id = rows[0][0]
            if contact_id in active_ids:
                data["data"][contact_id]["numbers"].append(number)
                continue
            active_ids.add(contact_id)
            data["data"][contact_id] = {"contact": rows[0], "numbers": [number]}
        return True

    def mode_date(self, data, param):
        data["input"] = param
        date = param.split("/")
        # if len(date) != 3:
        #     valid = False
        #     data["name"] = "split date"
        #     break
        # elif any(map(lambda x: (x) and (not x.isnumeric()), date)):
        #     valid = False
        #     data["name"] = "non-numerical date"
        #     break
        # data["data"], valid, _ = self._db.select("contact", {"date_of_birth": date})
        # data["name"] = "date contact"
        # break

    ##########################
    #  show → modes → table  #
    ##########################

    def change_to_group(self, data):
        for i, row in enumerate(data["data"].copy()):
            if row[4]:
                groups, _, _ = self._db.select("contact_group", {"id": row[4]})
                data["data"][i] = list(row)
                data["data"][i][4] = groups[0][1]
                data["data"][i] = tuple(data["data"][i])

    def add_plus_sign(self, data):
        for i, row in enumerate(data["data"].copy()):
            if row[1]:
                data["data"][i] = list(row)
                data["data"][i][1] = f"+{row[1]}"
                data["data"][i] = tuple(data["data"][i])

    ##################
    #  show → print  #
    ##################

    def print_show(self, data):
        space = " "
        dash = "-"

        name = data["name"]
        if "all" in name:
            all_constants = self.TO_PRINT["print"][name]
            spaces = all_constants["spaces"]

            columns_length = {"header": [], "values": []}
            for column_name in all_constants["columns"][self._language]:
                str_col_name = f" {column_name} "
                columns_length["header"].append(
                    {
                        "text": str_col_name,
                        "length": len(str_col_name)
                    }
                )

            for i, row in enumerate(data["data"]):
                t = 1
                columns_length["values"].append([])
                for j, column in enumerate(row):
                    if column == None:
                        column = ""
                    str_col = f" {column} "
                    columns_length["values"][i].append(str_col)
                    t += len(str_col) + 1
                    columns_length["header"][j]["length"] = max(columns_length["header"][j]["length"], len(str_col))

            total_length = 1
            for column in columns_length["header"]:
                total_length += column["length"] + 1

            print(f"\n{spaces}|", end="")
            for i, column in enumerate(columns_length["header"]):
                column_name = column["text"]
                current_spaces = space * (columns_length["header"][i]["length"] - len(column_name))
                print(f"{column_name}{current_spaces}|", end="")
            
            print(f"\n{spaces}{dash*total_length}")

            for i, row in enumerate(columns_length["values"]):
                print(f"{spaces}|", end="")
                for j, column_value in enumerate(row):
                    current_spaces = space * (columns_length["header"][j]["length"] - len(column_value))
                    print(f"{column_value}{current_spaces}|", end="")
                print()



        elif name == "no parameter":
            i = data["input"]
            print(self.TO_PRINT["print"]["no parameter"][self._language].replace("*?*", f"'{i}'"))
        print()

    ############
    #  insert  #
    ############

    def insert(parameters):
        pass

    def delete(parameters):
        pass

    ###########
    #  print  #
    ###########

    def wrong_command(self, option):
        print(self.TO_PRINT["print"]["wrong"][self._language].replace("*?*", f"'{option}'"))

    def print_options(self):
        print(self.TO_PRINT["print"]["options"][self._language])

    #######################
    #  print → constants  #
    #######################

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
                    "spaces": f"{space*6}",
                    "columns": {
                        "en": ["ID", "First name", "Last name", "Date of birth", "Group", "Street", "Number of descriptive", "City"],
                        "cz": ["ID", "Jméno", "Příjmení", "Datum narození", "Skupina", "Ulice", "Číslo popisné", "Město"],
                    }
                },
                "all contact_group": {
                    "spaces": f"{space*6}",
                    "columns": {
                        "en": ["ID", "Group"],
                        "cz": ["ID", "Skupina"]
                    }
                },
                "all prefix": {
                    "spaces": f"{space*6}",
                    "columns": {
                        "en": ["ID", "Prefix", "State"],
                        "cz": ["ID", "Předčíslí", "Stát"]
                    }
                },
                "all phone_number": {
                    "spaces": f"{space*6}",
                    "columns": {
                        "en": ["ID", "Prefix", "Number", "Contact"],
                        "cz": ["ID", "Předčíslí", "Číslo", "Kontakt"]
                    }
                },
                "no parameter": {
                    "en": "no parameter",
                    "cz": f"{space*6}Pro *?* chybí parameter"
                }
            }
        }

    #############
    #  general  #
    #############

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
