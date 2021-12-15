
# Program: dbapp.py
# Author: Tom Alexa


import sqlite3
from pathlib import Path

##############
#  contants  #
##############

# languages → (cz, en)
LANGUAGE = "cz"
DB_PATH = "database/"
DB_NAME = "contacts.db"


#########
#  App  #
#########

class App:
    OPTIONS = {
        "q": ("q", "quit", "e", "exit"),
        "l": ("l", "list"),
        "i": ("i", "insert"),
        "u": ("u", "update"),
        "d": ("d", "delete"),
        "h": ("h", "help")
    }
    PARAMETERS = {
        "l": {
            "table": ("-t", "--table"),
            "group": ("-g", "--group"),
            "number": ("-n", "--number"),
            "date": ("-d", "--date"),
        },
        "i": {
            "phone_number": ("phone_number", "number", "n")
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
        Input format: 'option' 'parameter' 'parameter', ex. l -t contact
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
        """
        Manage user input and do something
        """
        if option in self.OPTIONS["q"]:     # quit
            self.running = False
        elif option in self.OPTIONS["h"]:   # help
            self.print_options()
        elif option in self.OPTIONS["l"]:   # list
            self.show(parameters)
        elif option in self.OPTIONS["i"]:   # insert
            self.insert(parameters)
        elif option in self.OPTIONS["u"]:
            self.update(parameters)
        elif option in self.OPTIONS["d"]:   # delete
            self.delete(parameters)

    ##########
    #  show  #
    ##########

    def show(self, parameters):
        """
        User option 'L'
        Show something from the database
        """
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
                        self.mode_date(data, param)
                        break

                    else:
                        self.mode_name(data, param)
            else:
                if not data["input"]:
                    data["name"] = f"no parameter {mode}"
        else:
            self.mode_table(data, "contact")
        self.print_show(data)


    #########################
    #  show → subfunctions  #
    #########################

    def valid_option(self, option):
        """
        Check if option is in valid OPTIONS
        Return: True or False
        """
        for values in self.OPTIONS.values():
            if option in values: return True
        return False


    def get_parameter_mode(self, data, param):
        """
        Return mode for the next parameter
        """
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
        """
        Check if data['valid'] is True or False
        If so change some data
        """
        if not data["valid"]:
            data["input"] = param
            if error_name:
                data["name"] = error_name
            return False
        return True

    ##################
    #  show → modes  #
    ##################

    def mode_name(self, data, param):
        """
        Select contacts with first name or last name equal or similar with given parameter
        """
        rows, _, similar = self._db.select("contact", {"first_name": param, "last_name": param}, operant="OR")
        for row in rows:
            if row not in data["data"]:
                data["data"].append(row)

        if (data["name"] != "name similar contact") and not similar:
            data["name"] = "name same contact"
        else:
            data["name"] = "name similar contact"
        data["input"] += f"{param} "


    def mode_table(self, data, table_name):
        """
        Select rows from given table name
        """
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
            self.change_to_contact_name(data)
        elif table == "prefix":
            self.add_plus_sign(data)


    def mode_group(self, data, group_name):
        """
        Select contacts that belong to the group with given group name
        """
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
        self.change_to_group(data)

    def mode_number(self, data, param):
        """
        Select contacts with same or similar phone numbers
        """
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
            numbers, _, _ = self._db.select("phone_number", {"number": int(param), "prefix_id": data["input"][1:]}, similar=True)
        else:
            numbers, _, _ = self._db.select("phone_number", {"number": int(param)}, similar=True)
            data["input"] = param
        if not numbers:
            data["valid"] = False
            data["name"] = "no number"
            return True

        data["name"] = "number contact"
        data["data"] = []
        for number in numbers:
            if number[3]:
                rows, _, _ = self._db.select("contact", {"id": number[3]})
                data["data"].extend(rows)
        return True


    def mode_date(self, data, param):
        """
        Select contacts with same date of birth as given date (year, month or day)
        """
        data["input"] = param
        date = param.split("/")
        if len(date) != 3:
            data["valid"] = False
            data["name"] = "split date"
            return
        elif not any(date):
            data["valid"] = False
            data["name"] = "no-input date"
            return
        elif not all(map(lambda x: x.isnumeric(), filter(None, date))):
            data["valid"] = False
            data["name"] = "non-numerical date"
            return
        data["data"], _, _ = self._db.select("contact", {"date_of_birth": date})
        data["name"] = "date contact"
        self.change_to_group(data)


    ##########################
    #  show → modes → table  #
    ##########################

    def change_to_group(self, data):
        """
        Change group id to group name
        """
        for i, row in enumerate(data["data"].copy()):
            if row[4]:
                groups, _, _ = self._db.select("contact_group", {"id": row[4]})
                data["data"][i] = list(row)
                data["data"][i][4] = groups[0][1]
                data["data"][i] = tuple(data["data"][i])


    def change_to_contact_name(self, data):
        """
        Change contact id to contact first name and last name
        """
        for i, row in enumerate(data["data"].copy()):
            if row[3]:
                contacts, _, _ = self._db.select("contact", {"id": row[3]})
                first_name = contacts[0][1] if contacts[0][1] else ""
                last_name = contacts[0][2] if contacts[0][2] else ""
                space = " " if first_name and last_name else ""
                data["data"][i] = list(row)
                data["data"][i][3] = f"{first_name}{space}{last_name}"
                data["data"][i] = tuple(data["data"][i])


    def add_plus_sign(self, data):
        """
        Add '+' in front of prefix
        """
        for i, row in enumerate(data["data"].copy()):
            if row[1]:
                data["data"][i] = list(row)
                data["data"][i][1] = f"+{row[1]}"
                data["data"][i] = tuple(data["data"][i])


    ##################
    #  show → print  #
    ##################

    def print_show(self, data):
        """
        Print some data from the database
        """
        name = data["name"]
        if "all" in name:
            self.print_table(data)

        elif name == "name same contact":
            self.print_table(data, name="all contact")

        elif name == "name similar contact":
            self.print_table(data, name="all contact")

        elif name == "group contact":
            self.print_table(data, name="all contact")

        elif name == "similar group":
            self.print_table(data, name="all contact_group")

        elif name == "no group":
            self.print_table(data, name="all contact_group")

        elif name == "number contact":
            self.print_table(data, name="all contact")
            pass

        elif name == "not number":
            parameter = data["input"]
            print(self.TO_PRINT["print"]["not number"][self._language].replace("*?*", f"'{parameter}'"))

        elif name == "prefix contact":
            self.print_table(data, name="all phone_number", subdata=True)

        elif name == "similar prefix":
            self.print_table(data, name="all prefix", subdata=True)

        elif name == "split date":
            print(self.TO_PRINT["print"]["split date"][self._language])

        elif name == "non-numerical date":
            print(self.TO_PRINT["print"]["non-numerical date"][self._language])

        elif name == "date contact":
            self.print_table(data, name="all contact")

        elif "no parameter" in name:
            mode = name[13:]
            print(self.TO_PRINT["print"]["no parameter"][self._language].replace("*?*", f"'{mode}'"))

        elif not data["valid"]:
            if name == "parameter":
                parameter = data["input"][1:]
                print(self.TO_PRINT["print"]["parameter"][self._language].replace("*?*", f"'{parameter}'"))

            elif name == "table":
                table = data["input"]
                print(self.TO_PRINT["print"]["table"][self._language].replace("*?*", f"'{table}'"))
        print()


    def print_table(self, data, name=None, subdata=False):
        """
        Print table in the terminal
        """
        space = " "
        dash = "-"
        name = name if name else data["name"]

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
            print(f"{current_spaces}{column_name}|", end="")
        
        print(f"\n{spaces}{dash*total_length}")

        for i, row in enumerate(columns_length["values"]):
            print(f"{spaces}|", end="")
            for j, column_value in enumerate(row):
                current_spaces = space * (columns_length["header"][j]["length"] - len(column_value))
                print(f"{current_spaces}{column_value}|", end="")
            print()


    ############
    #  insert  #
    ############

    def insert(self, parameters):
        """
        User option "I"
        Insert something into the database
        """
        data = {"table": "contact", "data": []}
        if parameters:
            if parameters[0] in self.PARAMETERS["i"]["phone_number"]:
                data["table"] = "phone_number"
        self.insert_data(data)


    ###########################
    #  insert → subfunctions  #
    ###########################

    def insert_data(self, data):
        table = data["table"]
        if table == "contact":
            everything = {}
            first_name = self.ask_question("First name: ")
            last_name = self.ask_question("Last name: ")
            date_of_birth = self.ask_question("Date of birth: ", date=True)
            group_id = self.ask_question("Group ID: ", number=True)
            if group_id:
                groups = self._db.select("contact_group", {})[0]
                if groups: 
                    contact_group_ids = [x[0] for x in groups]
                    if group_id in contact_group_ids:
                        everything["group_id"] = group_id
                    else:
                        print("  Skupina neexistuje!\n")
                        group_id = self.ask_question("Group ID: ", number=True)
                else:
                    print("  Skupina neexistuje!\n")
                    group_id = self.ask_question("Group ID: ", number=True)
            street = self.ask_question("Street: ")
            nod = self.ask_question("Number of descriptive: ", number=True)
            city = self.ask_question("City: ")
            if first_name:
                everything["first_name"] = first_name
            if last_name:
                everything["last_name"] = last_name
            if date_of_birth:
                everything["date_of_birth"] = date_of_birth
            if street:
                everything["street"] = street
            if nod:
                everything["number_of_descriptive"] = nod
            if city:
                everything["city"] = city
            self._db.insert(table, everything)
        elif table == "contact_group":
            pass
        elif table == "phone_number":
            number = self.ask_question("Number: ", number=True, mandatory=True)
            prefix_id = self.ask_question("Kód země: ", number=True)
            contact_id = self.ask_question("Contact ID: ", number=True)
            everything = {"prefix_id": prefix_id}
            if number:
                everything["number"] = number
            if contact_id:
                contacts = self._db.select("contact", {})[0]
                if contacts: 
                    contact_ids = [x[0] for x in contacts]
                    if contact_id in contact_ids:
                        everything["contact_id"] = contact_id
                    else:
                        print("  Kontakt neexistuje!\n")
                else:
                    print("  Kontakt neexistuje!\n")
            self._db.insert(table, everything)
        elif table == "prefix":
            pass


    def ask_question(self, question, mandatory=False, date=False, number=False):
        while True:
            answer = input(question)
            if not mandatory and not answer:
                return answer
            if date:
                try:
                    a_split = answer.split("/")
                    if len(a_split) != 3:
                        raise ValueError
                    answer = f"{int(a_split[0]):04d}-{int(a_split[1]):02d}-{int(a_split[2]):02d}"
                    return answer
                except ValueError:
                    print("  Has to be a in format YYYY/MM/DD!\n")
                    continue
            if number:
                try:
                    answer = int(answer)
                    return answer
                except ValueError:
                    print("  Has to be a number!\n")
            else:
                return answer


    ############
    #  update  #
    ############

    def update(self, parameters):
        """
        User option "U"
        Insert something into the database
        """
        data = {"table": "contact", "data": []}
        if parameters:
            if parameters[0] in self.PARAMETERS["i"]["phone_number"]:
                data["table"] = "phone_number"
                id_to_update = self.ask_question("Upravit číslo pro [ID]: ", mandatory=True, number=True)
                numbers = self._db.select("phone_number", {})[0]
                if numbers: 
                    number_ids = [x[0] for x in numbers]
                    if id_to_update in number_ids:
                        number = self.ask_question("Number: ", number=True, mandatory=True)
                        prefix_id = self.ask_question("Kód země: ", number=True)
                        contact_id = self.ask_question("Contact ID: ", number=True)
                        everything = {"prefix_id": prefix_id}
                        if number:
                            everything["number"] = number
                        if contact_id:
                            contacts = self._db.select("contact", {})[0]
                            if contacts: 
                                contact_ids = [x[0] for x in contacts]
                                if contact_id in contact_ids:
                                    everything["contact_id"] = contact_id
                                else:
                                    print("  Kontakt neexistuje!\n")
                                    return
                            else:
                                print("  Kontakt neexistuje!\n")
                                return
                    else:
                        print("  Číslo neexistuje!\n")
                        return
                else:
                    print("  Číslo neexistuje!\n")
                    return
        else:
            id_to_update = self.ask_question("Upravit kontakt pro [ID]: ", mandatory=True, number=True)
            contacts = self._db.select("contact", {})[0]
            if contacts:
                contact_ids = [x[0] for x in contacts]
                if id_to_update in contact_ids:
                    everything = {}
                    first_name = self.ask_question("First name: ")
                    last_name = self.ask_question("Last name: ")
                    date_of_birth = self.ask_question("Date of birth: ", date=True)
                    group_id = self.ask_question("Group ID: ", number=True)
                    if group_id:
                        groups = self._db.select("contact_group", {})[0]
                        if groups: 
                            contact_group_ids = [x[0] for x in groups]
                            if group_id in contact_group_ids:
                                everything["group_id"] = group_id
                            else:
                                print("  Skupina neexistuje!\n")
                                group_id = self.ask_question("Group ID: ", number=True)
                        else:
                            print("  Skupina neexistuje!\n")
                            group_id = self.ask_question("Group ID: ", number=True)
                    street = self.ask_question("Street: ")
                    nod = self.ask_question("Number of descriptive: ", number=True)
                    city = self.ask_question("City: ")
                    if first_name:
                        everything["first_name"] = first_name
                    if last_name:
                        everything["last_name"] = last_name
                    if date_of_birth:
                        everything["date_of_birth"] = date_of_birth
                    if street:
                        everything["street"] = street
                    if nod:
                        everything["number_of_descriptive"] = nod
                    if city:
                        everything["city"] = city
                else:
                    print("  Kontakt neexistuje!\n")
                    return
            else:
                print("  Kontakt neexistuje!\n")
                return
        self._db.update(data["table"], everything, id_to_update)


    ############
    #  delete  #
    ############

    def delete(self, parameters):
        """
        User option "D"
        Insert something into the database
        """
        data = {"table": "contact", "data": []}
        if parameters:
            if parameters[0] in self.PARAMETERS["i"]["phone_number"]:
                data["table"] = "phone_number"
        self.delete_data(data)


    def delete_data(self, data):
        table = data["table"]
        if table == "contact":
            id_to_delete = self.ask_question("Contact ID: ", mandatory=True, number=True)
            contacts = self._db.select("contact", {})[0]
            if contacts: 
                contact_ids = [x[0] for x in contacts]
                if id_to_delete in contact_ids:
                    self._db.delete("contact", id_to_delete)
                else:
                    print("  Kontakt neexistuje!\n")
            else:
                print("  Kontakt neexistuje!\n")
        elif table == "phone_number":
            id_to_delete = self.ask_question("Phone number ID: ", mandatory=True, number=True)
            phone_numbers = self._db.select("phone_number", {})[0]
            if phone_numbers: 
                phone_number_ids = [x[0] for x in phone_numbers]
                if id_to_delete in phone_number_ids:
                    self._db.delete("phone_number", id_to_delete)
                else:
                    print("  Číslo neexistuje!\n")
            else:
                print("  Číslo neexistuje!\n")

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
                    "cz": f"{spaces_options}{dash_options}\n{spaces_options}| H {comma*16} ukáže tuto tabulku{space*40}|\n{spaces_options}| L (jméno) {comma*8} ukáže kontakt podle jména nebo podobné kontakty{space*11}|\n{spaces_options}| L -n (číslo) {comma*5} ukáže kontakty podle čísla nebo podobné kontakty{space*10}|\n{spaces_options}| L -g (skupina) {comma*3} ukáže kontakty ve skupině{space*33}|\n{spaces_options}| L -t (tabulka) {comma*3} ukáže všechny řádky v tabulce{space*29}|\n{spaces_options}| L -d (datum) {comma*5} ukáže kontakty podle data narození → formát: YYYY/MM/DD{space*3}|\n{spaces_options}|{space*60}den: //DD{space*9}|\n{spaces_options}|{space*58}měsíc: /MM/{space*9}|\n{spaces_options}|{space*60}rok: YYYY//{space*7}|\n{spaces_options}| I {comma*16} vloží kontakt do tabulky{space*34}|\n{spaces_options}| I (tabulka) {comma*6} vloží řádek do tabulky{space*36}|\n{spaces_options}| D {comma*16} odstraní kontakt{space*42}|\n{spaces_options}| D (tabulka) {comma*6} odstraní řádek z tabulky{space*34}|\n{spaces_options}| U {comma*16} uprav kontakt{space*45}|\n{spaces_options}| U (tabulka) {comma*6} uprav řádek z tabulky{space*37}|\n{spaces_options}| Q {comma*16} ukončí aplikaci{space*43}|\n{spaces_options}{dash_options}",
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
                    "cz": f"{space*6}Pro *?* chybí parameter!"
                },
                "parameter": {
                    "en": "wrong parameter",
                    "cz": f"{space*6}Parameter *?* neexistuje!"
                },
                "table": {
                    "en": "wrong table",
                    "cz": f"{space*6}Tabulka *?* neexistuje!\n{space*6}Zkus 'contact', 'group', 'number', 'prefix'."
                },
                "not number": {
                    "en": "not number",
                    "cz": f"{space*6}Parameter *?* není číslo!"
                },
                "split date": {
                    "en": f"{space*6}Not a right format for a date!",
                    "cz": f"{space*6}Datum je zadané ve špatném formátu!"
                },
                "non-numerical date": {
                    "en": f"{space*6}Not a right format for a date!",
                    "cz": f"{space*6}Datum musí být zadané v číselném formátu!"
                },
            }
        }


    #############
    #  general  #
    #############

    def close(self):
        self._db.close()


#####################
#  ContactDatabase  #
#####################

class ContactDatabase:
    TABLES = {
        "contact": "id, first_name, last_name, date_of_birth, group_id, street, number_of_descriptive, city",
        "contact_group": "id, name",
        "prefix": "id, prefix, state",
        "phone_number": "id, prefix_id, number, contact_id"
    }

    def __init__(self):
        self.db_path = Path(f"{Path(__file__).parent.resolve()}/{DB_PATH}{DB_NAME}")
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


    def insert(self, table, parameters: dict):
        columns = ", ".join(parameters.keys())
        values = ""
        for value in parameters.values():
            if type(value) is int:
                values += f"{value}, "
            else:
                values += f"'{value}', "
        values = values[:-2]
        self.cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({values});")
        self.connection.commit()


    def update(self, table, parameters: dict, id_to_update):
        to_update = ""
        for column, value in parameters.items():
            if type(value) is int:
                to_update += f"{column} = {value}, "
            else:
                to_update += f"{column} = '{value}', "
        to_update = to_update[:-2]
        self.cursor.execute(f"UPDATE {table} SET {to_update} WHERE id = {id_to_update};")


    def delete(self, table, id_to_delete):
        self.cursor.execute(f"DELETE FROM {table} WHERE id = {id_to_delete}")
        self.connection.commit()


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
        self.cursor.execute("PRAGMA foreign_keys = OFF;")
        self.connection.commit()

        inserts = [
            """INSERT INTO contact_group (name) VALUES
                ("family"), ("friends"), ("work")
            """
        ]
        for ins in inserts:
            self.cursor.execute(ins)
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
