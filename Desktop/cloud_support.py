# coding: utf-8

import requests
import json

from widgets import*

api_key = "51c63f31-4635-11eb-bff2-0242ac110002"
school_list_id = "2da280f42766"
school_ids_id = "f53b6f4631d6"

def fetch_list_of_schools():
    print("fetching list of schools")
    try:
        response = requests.get(f"https://json.extendsclass.com/bin/{school_list_id}")
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return 1
        else:
            return json.loads(response.text)["school_list"]
    except Exception:
        dialog("Une erreur est survenue lors du téléchargement de la liste des écoles", "Erreur")
        return 1


def creer_ecole(ecole, pwd):
    list_of_schools = fetch_list_of_schools()
    if list_of_schools == 1:
        return False

    try:
        # creating new json file for the created school
        response = requests.post("https://json.extendsclass.com/bin",
                                headers={"Api-key": api_key, "Private": "true",
                                         "Security-key": pwd})
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False

        new_school_id = json.loads(response.text)["id"]

        # fetching the school ids json file
        response = requests.get(f"https://json.extendsclass.com/bin/{school_ids_id}")
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False

        school_ids_dict = json.loads(response.text)

        # registering the id of created school
        school_ids_dict[ecole] = new_school_id

        response = requests.put(f"https://json.extendsclass.com/bin/{school_ids_id}",
                                headers={"Api-key": api_key},
                                data=json.dumps(school_ids_dict))
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False

        # updating current school named (local)
        with open("school_name.txt", "w") as f:
            f.write(ecole)

        # creating/erasing register local file
        open("registre_certificats.json", "w").close()


        # updating school list json file
        school_list_dict = {"school_list": list_of_schools + [ecole]}
        response = requests.put(f"https://json.extendsclass.com/bin/{school_list_id}",
                    headers={"Api-key": api_key},
                    data=json.dumps(school_list_dict))

        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False

        return True

    except Exception as error:
        print(repr(error))
        dialog("Une erreur est survenue lors de la création du registre", "Error")
        return False




def supprimer_registre(ecole):
    pwd, ok = QInputDialog.getText(None,
                                   "Authorisation requise",
                                   "Enter password", QLineEdit.Password)
    if not ok:
        return False

    try:
        # fetching the school id from json file
        response = requests.get(f"https://json.extendsclass.com/bin/{school_ids_id}")
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False

        d = json.loads(response.text)
        school_id = json.loads(response.text)[ecole]

        # checking password
        response = requests.get(f"https://json.extendsclass.com/bin/{school_id}",
                                   headers={"Api-key": api_key,
                                            "Security-key": pwd})
        if not response:
            dialog("Mot de passe erronné", "Erreur d'authenficiation")
            return False
    except IOError as error:
        dialog("Une erreur est survenue lors de la suppression du registre. Veuillez réessayer.", "Error")
        print(repr(error))
        return False

    if confirm(f"Supprimer le registre de certificats de l'école {ecole} (toutes les données seront perdues) ?"):
        try:
            response = requests.delete(f"https://json.extendsclass.com/bin/{school_id}",
                                       headers={"Api-key": api_key,
                                                "Security-key": pwd})
            if not response:
                dialog(json.loads(response.text)["message"], str(response))
                return False

            list_of_schools = fetch_list_of_schools()
            list_of_schools.remove(ecole)
            ds = {"school_list": list_of_schools}
            response = requests.put(f"https://json.extendsclass.com/bin/{school_list_id}",
                        headers={"Api-key": api_key},
                        data=json.dumps(ds))
            if not response:
                dialog(json.loads(response.text)["message"], str(response))
                return False

            open("registre_certificats.json", "w").close()
            open("school_name.txt", "w").close()
            del d[ecole]

            # updating school ids json file
            response = requests.put(f"https://json.extendsclass.com/bin/{school_ids_id}",
                                    headers={"Api-key": api_key},
                                    data=json.dumps(d))
            if not response:
                dialog(json.loads(response.text)["message"], str(response))
                return False

            return True
        except IOError as error:
            dialog("Une erreur est survenue lors de la suppression du registre. Veuillez réessayer.", "Error")
            print(repr(error))
            return False


def download_registre(ecole, pwd):
    try:
        # fetching the school id from json file
        response = requests.get(f"https://json.extendsclass.com/bin/{school_ids_id}")
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False

        school_id = json.loads(response.text)[ecole]

        # fetching json data for the school to load
        response = requests.get(f"https://json.extendsclass.com/bin/{school_id}",
                                headers={"Api-key": api_key,
                                         "Security-key": pwd})
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False

        with open("registre_certificats.json", "w") as f:
            f.write(response.text)
        with open("school_name.txt", "w") as f:
            f.write(ecole)
        with open("p.rc", "w") as f:
            f.write(pwd)
        return True

    except IOError:
        dialog("Une erreur est survenue lors du chargement du registre. Veuillez réessayer.", "Error")
        return False


def upload_registre():
    """Uploads local registre file to cloud"""
    try:
        with open("p.rc", "r") as f:
            pwd = f.read()
        pwd_prompted = False
    except FileNotFoundError:
        pwd, ok = QInputDialog.getText(None, "Authorisation requise", "Enter password")
        if not ok:
            return
        pwd_prompted = True


    with open("school_name.txt", "r") as f:
        ecole = f.read()

    # fetching the school id from json file
    response = requests.get(f"https://json.extendsclass.com/bin/{school_ids_id}")
    if not response:
        dialog(json.loads(response.text)["message"], str(response))
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
            dialog(json.loads(response.text)["message"], str(response))
            return False
        if pwd_prompted:
            with open("p.rc", "w") as f:
                f.write(pwd)
        return True
    except Exception:
        dialog("Une erreur est survenue lors de la mise en ligne du registre. Veuillez réessayer.", "Error")
        return False

