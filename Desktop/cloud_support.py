# coding: utf-8

import requests
import json

from widgets import*

api_key = "51c63f31-4635-11eb-bff2-0242ac110002"
school_list_id = "2da280f42766"

def fetch_list_of_schools():
    print("fetching list of schools")
    try:
        response = requests.get(f"https://json.extendsclass.com/bin/{school_list_id}",
                                     headers={"Api-key": api_key})
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
        response = requests.post("https://json.extendsclass.com/bin",
                                headers={"Api-key": api_key, "Private": "true",
                                         "Security-key": pwd})
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False
        else:
            with open("json_local_school_ids.json", "r") as f:
                d = json.load(f)

            d[ecole] = json.loads(response.text)["id"]

            with open("json_local_school_ids.json", "w") as f:
                json.dump(d, f)

            with open("school_name.txt", "w") as f:
                f.write(ecole)

            open("registre_certificats.json", "w").close()

            d = {"school_list": list_of_schools + [ecole]}
            response = requests.put(f"https://json.extendsclass.com/bin/{school_list_id}",
                        headers={"Api-key": api_key},
                        data=json.dumps(d))

            if not response:
                dialog(json.loads(response.text)["message"], str(response))
                return False

            return True

    except Exception as error:
        print(repr(error))
        dialog("Une erreur est survenue lors de la création du registre", "Error")
        return False


def charger_ecole(ecole, pwd):
    with open("json_local_school_ids.json", "r") as f:
        school_id = json.load(f)[ecole]

    try:
        response = requests.get(f"https://json.extendsclass.com/bin/{school_id}",
                                headers={"Api-key": api_key,
                                         "Security-key": pwd})
        if not response:
            dialog(json.loads(response.text)["message"], str(response))
            return False
        else:
            with open("registre_certificats.json", "w") as f:
                f.write(response.text)
            with open("school_name.txt", "w") as f:
                f.write(ecole)
            with open("p.rc", "w") as f:
                f.write(pwd)
            return True
    except Exception:
        dialog("Une erreur est survenue lors du chargement du registre. Veuillez réessayer.", "Error")
        return False



def supprimer_registre(ecole):
    pwd, ok = QInputDialog.getText(None,
                                   "Authorisation requise",
                                   "Enter password", QLineEdit.Password)
    if not ok:
        return False

    with open("json_local_school_ids.json", "r") as f:
        d = json.load(f)
        school_id = d[ecole]
    try:
        response = requests.get(f"https://json.extendsclass.com/bin/{school_id}",
                                   headers={"Api-key": api_key,
                                            "Security-key": pwd})
        if not response:
            dialog("Mot de passe erronné", "Erreur d'authenficiation")
            return False
    except Exception:
        dialog("Une erreur est survenue lors de la suppression du registre. Veuillez réessayer.", "Error")
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
            with open("json_local_school_ids.json", "w") as f:
                json.dump(d, f)
            return True
        except Exception:
            dialog("Une erreur est survenue lors de la suppression du registre. Veuillez réessayer.", "Error")
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
    with open("json_local_school_ids.json", "r") as f:
        school_id = json.load(f)[ecole]
    with open("registre_certificats.json", "r") as f:
        jsonable = f.read()
    try:
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

