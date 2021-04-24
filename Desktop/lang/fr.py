# coding: utf-8

# Strings in French

class StringsFR:
    def __init__(self):
        self.code = "fr"
        self.name = "Français"
        self.TITLE = "Registre des certificats"
        self.PARAMETERS_BUTTON = "Paramètres"
        self.PRINT_BUTTON = "Imprimer"
        self.MEMBER_CB = "Membre"
        self.CATEG_CB = "Catégorie"
        self.CERT_CB = "Certificat"
        self.AWARD_CERTIFICATE = "Décerner certificat"
        self.REVOKE_CERTIFICATE = "Retirer certificat"
        self.MAKE_CERTIFICATOR_BUTTON = "Rendre Certificateur"
        self.REINITIALIZE_BUTTON = "Réinitialiser"
        self.SAVED = "Enregistré"
        self.SAVING = "Enregistrement..."
        self.SYNCHRONIZING = "Synchronisation..."
        self.INVALID_REGISTER_VALUE = "Valeur invalide dans le registre"
        self.DELETE_CATEGORY_Q = "Supprimer catégorie ?"
        self.ADVANCED = "Avancé"
        self.HIDE = "Masquer"
        self.CREATE_LOAD_REGISTER = "Créer/Charger registre"
        self.DELETE_REGISTER = "Supprimer registre"
        self.MEMBER_LIST = "Liste des membres :"
        self.ADD_MEMBER = "Ajouter membre :"
        self.FIRST_NAME = "Prénom"
        self.LAST_NAME = "Nom"
        self.VALIDATE = "Valider"
        self.REMOVE_MEMBER = "Retirer le membre"
        self.CATEGORIES = "Catégories :"
        self.CERTIFICATES = "Certificats :"
        self.ADD_CERTIFICATE = "Ajouter certificat :"
        self.CATEGORY = "Catégorie"
        self.CERTIFICATE_NAME = "Nom du certificat"
        self.DELETE_CERTIFICATE = "Supprimer Certificat"
        self.DELETE_CATEGORY = "Supprimer Catégorie"
        self.CLICK_HERE_TO_BEGIN = "Cliquez ici pour commencer : "
        self.ERROR = "Erreur"
        self.LOAD_OR_CREATE_REGISTER = "Charger ou créer un registre"
        self.SCHOOL = "Ecole :"
        self.ENTER_NAME = "Entrer un nom"
        self.PASSWORD = "Mot de passe :"
        self.CONFIRM_PASSWORD = "Confirmer mot de passe :"
        self.PASSWORDS_DONT_MATCH = "Les mots de passe ne correspondent pas"
        self.CREATE_REGISTER = "Créer registre"
        self.LOAD_REGISTER = "Charger registre"
        self.ERROR_DURING_SCHOOL_LIST_DOWNLOAD = "Une erreur est survenue lors du téléchargement de la liste des écoles"
        self.ERROR_WHEN_CREATING_REGISTER = "Une erreur est survenue lors de la création du registre"
        self.AUTHORIZATION_REQUIRED = "Authorisation requise"
        self.ENTER_PASSWORD = "Entrer mot de passe"
        self.WRONG_PASSWORD = "Mot de passe erronné"
        self.AUTHENTICATION_ERROR = "Erreur d'authenficiation"
        self.ERROR_DURING_REGISTER_DELETION = "Une erreur est survenue lors de la suppression du registre. Veuillez réessayer."
        self.ERROR_WHILE_LOADING_REGISTER = "Une erreur est survenue lors du chargement du registre. Veuillez réessayer."
        self.ERROR_WHILE_UPLOADING_REGISTER = "Une erreur est survenue lors de la mise en ligne du registre. Veuillez réessayer."
        self.REGISTER = "Registre"
        self.REGISTER_OF_CERTIFICATES = "Registre des certificats"
        self.CANT_OPEN_LIBREOFFICE = "Impossible d'ouvrir LibreOffice. Veuillez ouvrir le fichier manuellement"
        self.CHECK_INTERNET_CONNECTION = "Veuillez vérifier votre connexion internet."
        self.CONFIRM = "Confirmer"
        self.CONFIRMATION = "Confirmation"
        self.INFORMATION = "Information"
        self.SELECT_LANGUAGE = "Sélectionner la langue"
        self.LANGUAGE = "Langue : "

    def REMOVE_CERTIFICATE_FROM(self, m, c):
        return f"Retirer le certificat {c}, à {m} ?"

    def AWARD_CERTIFICATE_TO(self, m, c):
        return f"Décerner le certificat {c} à {m} ?"

    def MAKE_CERTIFICATOR(self, m, c):
        return f"Rendre {m} certificateur\xb7rice pour le certificat {c} ?"

    def CLEAR_HISTORY(self, m, c):
        return f"Effacer l'historique de {m} pour le certificat {c} ?"

    def MEMBER_ALREADY_EXISTS(self, firstname, surname):
        return f"Il existe déjà un membre nommé {firstname} {surname}."

    def CERTIFICATE_ALREADY_EXISTS(self, c, cat):
        return f"Il existe déjà un certificat nommé {c} dans la catégorie {cat}"

    def DOESNT_HAVE_CERTIFICATE(self, m, c):
        return f"{m} n'a pas le certificat {c}"

    def DOESNT_HAVE_CERTIFICATE_ANYMORE(self, m, c):
        return f"{m} n'a plus le certificat {c}"

    def IS_CERTIFICATOR(self, m, c):
        return f"{m} est certificateur\xb7ice pour le certificat {c}."

    def HAS_CERTIFICATE(self, m, c):
        return f"{m} a le certificat {c}."

    def HAS_CERTIFICATES(self, m, l):
        msg = ""
        if len(l) == 1: msg = f"{m} a le certificat : {l[0]}"
        elif len(l) >= 2:
            msg = f"{m} a les certificats : "
            for i in range(len(l)):
                if i < len(l) - 1:
                    msg += f"{l[i]}, "
                else:
                    msg += f"et {l[i]}."

        return msg

    def CERTIFICATORS_ARE(self, c, certificators):
        msg = f"Les certificateurs pour le certificat {c} sont : "
        if len(certificators) == 1: msg += certificators[0]
        else:
            for i in range(len(certificators)):
                if i < len(certificators) - 1:
                    msg += f"{certificators[i]}, "
                else:
                    msg += f"et {certificators[i]}."
        if not certificators:
            msg = f"Il n'y a pas encore de certificateurs pour le certificat {c}."

    def X_CAT_CERTIFICATES(self, category):
        return f"Certificats {category} :"

    def CREATE_REGISTER_FOR_SCHOOL(self, school):
        return f"Créer un registre des certificats pour l'école {school} ?"

    def REGISTER_FOR_SCHOOL_HAS_BEEN_CREATED(self, school):
        return f"Le registre pour l'école {school} a bien été créé."

    def REGISTER_FOR_SCHOOL_HAS_BEEN_LOADED(self, school):
        return f"Le registre pour l'école {school} a bien été chargé."

    def DELETE_REGISTER_FOR_SCHOOL(self, school):
        return f"Supprimer le registre de certificats de l'école {school} (toutes les données seront perdues) ?"

