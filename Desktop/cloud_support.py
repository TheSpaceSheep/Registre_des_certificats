# coding: utf-8
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QInputDialog, QLineEdit
# from PyQt5.QtCore import *
import requests
import json
import language_selector as ls

import widgets
from registre_manager import Registre

api_key = "51c63f31-4635-11eb-bff2-0242ac110002"
school_list_id = "2da280f42766"
school_ids_id = "f53b6f4631d6"

def fetch_list_of_schools():
    """retrieves list of existing schools that have an online register"""
    try:
        response = requests.get(f"https://json.extendsclass.com/bin/{school_list_id}")
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return 1
        else:
            return json.loads(response.text)["school_list"]
    except Exception:
        widgets.dialog(ls.strings.ERROR_DURING_SCHOOL_LIST_DOWNLOAD, ls.strings.ERROR)
        return 1


def creer_ecole(ecole, pwd):
    """Creates new empty register and corresponding json file in the cloud"""
    list_of_schools = fetch_list_of_schools()
    if list_of_schools == 1:
        return False

    try:
        registre = Registre()
        registre.enregistrer()
        with open("registre_certificats.json", "r") as f:
            jsonable = f.read()
        # creating new json file for the created school
        response = requests.post("https://json.extendsclass.com/bin",
                                headers={"Api-key": api_key, "Private": "true",
                                         "Security-key": pwd}, data=jsonable)
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False

        new_school_id = json.loads(response.text)["id"]

        # fetching the school ids json file
        response = requests.get(f"https://json.extendsclass.com/bin/{school_ids_id}")
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False

        school_ids_dict = json.loads(response.text)

        # registering the id of created school
        school_ids_dict[ecole] = new_school_id

        response = requests.put(f"https://json.extendsclass.com/bin/{school_ids_id}",
                                headers={"Api-key": api_key},
                                data=json.dumps(school_ids_dict))
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False

        # updating current school name (local)
        with open("school_name.txt", "w") as f:
            f.write(ecole)

        with open("p.rc", "w") as f:
            f.write(pwd)

        # creating/erasing register local file
        open("registre_certificats.json", "w").close()

        # updating school list json file
        school_list_dict = {"school_list": list_of_schools + [ecole]}
        response = requests.put(f"https://json.extendsclass.com/bin/{school_list_id}",
                    headers={"Api-key": api_key},
                    data=json.dumps(school_list_dict))

        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False

        return True

    except Exception as error:
        print(repr(error))
        widgets.dialog(ls.strings.ERROR_WHEN_CREATING_REGISTER, ls.strings.ERROR)
        return False


def supprimer_registre(ecole):
    """deletes a register in the cloud and associated local files"""
    pwd, ok = QInputDialog.getText(None,
                                   ls.strings.AUTHORIZATION_REQUIRED,
                                   ls.strings.ENTER_PASSWORD, QLineEdit.Password)
    if not ok:
        return False

    try:
        # fetching the school id from json file
        response = requests.get(f"https://json.extendsclass.com/bin/{school_ids_id}")
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False

        d = json.loads(response.text)
        school_id = json.loads(response.text)[ecole]

        # checking password
        response = requests.get(f"https://json.extendsclass.com/bin/{school_id}",
                                   headers={"Api-key": api_key,
                                            "Security-key": pwd})
        if not response:
            widgets.dialog(ls.strings.WRONG_PASSWORD, ls.strings.AUTHENTICATION_ERROR)
            return False

    except Exception as error:
        widgets.dialog(ls.strings.ERROR_DURING_REGISTER_DELETION, ls.strings.ERROR)
        print(repr(error))
        return False

    if widgets.confirm(ls.strings.DELETE_REGISTER_FOR_SCHOOL(ecole)):
        try:
            response = requests.delete(f"https://json.extendsclass.com/bin/{school_id}",
                                       headers={"Api-key": api_key,
                                                "Security-key": pwd})
            if not response:
                widgets.dialog(json.loads(response.text)["message"], str(response))
                return False

            # removing school name from list of schools online file
            list_of_schools = fetch_list_of_schools()
            list_of_schools.remove(ecole)
            ds = {"school_list": list_of_schools}
            response = requests.put(f"https://json.extendsclass.com/bin/{school_list_id}",
                        headers={"Api-key": api_key},
                        data=json.dumps(ds))
            if not response:
                widgets.dialog(json.loads(response.text)["message"], str(response))
                return False

            # erasing local files
            open("registre_certificats.json", "w").close()
            open("school_name.txt", "w").close()
            del d[ecole]

            # updating school ids json file
            response = requests.put(f"https://json.extendsclass.com/bin/{school_ids_id}",
                                    headers={"Api-key": api_key},
                                    data=json.dumps(d))
            if not response:
                widgets.dialog(json.loads(response.text)["message"], str(response))
                return False

            return True
        except IOError as error:
            widgets.dialog(ls.strings.ERROR_DURING_REGISTER_DELETION, ls.strings.ERROR)
            print(repr(error))
            return False


def download_registre(ecole, pwd):
    """downloads a register for a school from the cloud and writes it to the default local file"""
    try:
        # fetching the school id from json file
        response = requests.get(f"https://json.extendsclass.com/bin/{school_ids_id}")
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False

        school_id = json.loads(response.text)[ecole]

        # fetching json data for the school to load
        response = requests.get(f"https://json.extendsclass.com/bin/{school_id}",
                                headers={"Api-key": api_key,
                                         "Security-key": pwd})
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False

        # creating/overwriting local files
        with open("registre_certificats.json", "w") as f:
            f.write(response.text)
        with open("school_name.txt", "w") as f:
            f.write(ecole)
        with open("p.rc", "w") as f:
            f.write(pwd)
        return True

    except IOError:
        widgets.dialog(ls.strings.ERROR_WHILE_LOADING_REGISTER, ls.strings.ERROR)
        return False


def upload_registre():
    """Uploads local register file to cloud"""
    try:
        with open("p.rc", "r") as f:
            pwd = f.read()
        pwd_prompted = False
    except FileNotFoundError:
        pwd, ok = QInputDialog.getText(None, ls.strings.AUTHORIZATION_REQUIRED, ls.strings.ENTER_PASSWORD)
        if not ok:
            return
        pwd_prompted = True

    with open("school_name.txt", "r") as f:
        ecole = f.read()

    try:
        # fetching the school id from json file
        response = requests.get(f"https://json.extendsclass.com/bin/{school_ids_id}")
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False
    except Exception:
        widgets.dialog(ls.strings.ERROR_WHILE_UPLOADING_REGISTER, ls.strings.ERROR)
        return False

    d = json.loads(response.text)
    school_id = json.loads(response.text)[ecole]

    with open("registre_certificats.json", "r") as f:
        jsonable = f.read()
    try:
        # updating register json file for the school
        response = requests.put(f"https://json.extendsclass.com/bin/{school_id}",
                                   headers={"Api-key": api_key,
                                            "Security-key": pwd}, data=jsonable)
        if not response:
            widgets.dialog(json.loads(response.text)["message"], str(response))
            return False
        if pwd_prompted:
            with open("p.rc", "w") as f:
                f.write(pwd)
        return True
    except Exception:
        widgets.dialog(ls.strings.ERROR_WHILE_UPLOADING_REGISTER, ls.strings.ERROR)
        return False

