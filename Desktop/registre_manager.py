# coding: utf-8
import os
import json

class Membre:
    """
    Holds basic school member information

    Attributes
    ----------
    prenom: str
        first name of the member
    nom: str
        last name of the member
    id: str
        unique identification for the member (generated
        based on the first and last name) this is the string
        that will be displayed throughout the application
    """
    def __init__(self, prenom, nom):
        self.prenom = prenom
        self.nom = nom
        self.id = prenom

    def __eq__(self, other):
        if not isinstance(other, Membre):
            return NotImplemented
        return self.prenom == other.prenom and self.nom == other.nom

    def __str__(self):
        return self.prenom + self.nom

    def __hash__(self):
        return hash(str(self))


class Certificat:
    """
    Holds basic information for a Certificate

    Attributes
    ----------
    nom: str
        name of the certificate. Must be unique in a register.
    categorie: str
        certificates are regrouped in categories,
        to help the user identify them
    """
    def __init__(self, nom, categorie):
        self.nom = nom
        self.categorie = categorie

    def __eq__(self, other):
        if not isinstance(other, Certificat):
            return NotImplemented
        return self.nom == other.nom and self.categorie == other.categorie

    def __str__(self):
        return self.nom + self.categorie

    def __hash__(self):
        return hash(str(self))


class Registre:
    """
    Class to represent and modify a register.

    Attributes
    ----------

    membres: list of "Membre" objects
        list of all members in the school

    certificats: list of "Certificat" objects
        list of all certificates in the register

    registre: dict [Membre, Certificat] -> value
        dictionary that tells how a member relates to a certificate

    categories: dict [category] -> list of certificates
        lists of "Certificat" objects for each category



    A member can relate to a certificate in the following ways:
        - NonCertifie 0 : The member never had the certificate
        - Certifie 1 : The member has the certificate
        - Certificateur -1: The member can award the certificate to someone else
        - CertificatPerdu -2: The member does not have the certificate anymore

        note: it possible for a register value to be more than 1, to account for different
        "certificate levels" though the rest of the app does not implement this functionality yet.
    """
    NonCertifie = 0
    Certifie = 1
    Certificateur = -1
    CertificatPerdu = -2

    def __init__(self):
        self.membres = []
        self.certificats = []
        self.registre = {}
        self.categories = {}


    def ajouter_membre(self, prenom, nom):
        """Adds a new member to the register"""
        m = Membre(prenom, nom)

        # S'ils ont le même prenom, rajouter quelques lettres du nom de famille
        duplicates = []
        for n in self.membres:
            if n.prenom == m.prenom:
                if n.nom == m.nom:
                    return f"Il existe déjà un membre nommé {n.prenom} {n.nom}."
                duplicates.append(n)

        if duplicates:
            unambiguous_id(duplicates+[m])

        self.membres.append(m) if m not in self.membres else self.membres
        for c in self.certificats:
            self.registre[m, c] = Registre.NonCertifie
        
        self.trier_membres()
        return m

    def ajouter_membres(self, liste_membres):
        """Adds a list of new member to the register"""
        for (prenom, nom) in liste_membres:
            self.ajouter_membre(prenom, nom)

    def ajouter_certificat(self, nom, categorie):
        """Adds a certificate to the register
        (category is created if it does not yet exist)"""
        c = Certificat(nom, categorie)
        for cert in self.certificats:
            # different certificats cannot have the same name 
            if cert.nom == c.nom:
                return f"Il existe déjà un certificat nommé {nom} dans la catégorie {cert.categorie}."

        self.certificats.append(c)
        if c.categorie in self.categories:
            self.categories[c.categorie].append(c.nom)
        else:
            self.categories[c.categorie] = [c.nom]

        for m in self.membres:
            self.registre[m, c] = Registre.NonCertifie

        self.trier_certificats()


    def ajouter_certificats(self, liste_certificats):
        """Adds a list of certificates to the register"""
        for (nom, categorie) in liste_certificats:
            self.ajouter_certificat(nom, categorie)


    def supprimer_membre(self, m):
        """removes member from register (and all associated register entries)"""
        if m in self.membres:
            self.membres.remove(m)
            for c in self.certificats:
                del self.registre[m, c]
            duplicates = []
            for n in self.membres:
                if n.prenom == m.prenom:
                    n.id = n.prenom
                    duplicates.append(n)

            if len(duplicates) >= 2:
                unambiguous_id(duplicates)

            return True
        else:
            return False

    def supprimer_certificat(self, c):
        """deletes a certificate from register (and all associated register entries)"""
        if c in self.certificats:
            self.certificats.remove(c)
            for m in self.membres:
                del self.registre[m, c]
            return True
        else:
            return False

    def supprimer_categorie(self, cat):
        """deletes a category from register (and all associated certificates and register entries)"""
        for c in self.get_certificats(cat):
            self.supprimer_certificat(c)

        del self.categories[cat]


    def decerner_certificat(self, membre, certificat, niveau):
        """Changes the way the member relates to the certificate

        Parameters
        ----------
        membre: Membre
        certificat: Certificat
        niveau: int
            0 : the member never had the certificate
           -1 : the member can award the certificate to someone else
           -2 : the member has lost the certificate
           1, 2, ... : the member has the certificate with level ..."""
        self.registre[membre, certificat] = niveau

    def a_le_certificat(self, membre, certificat):
        """
        Returns
        -----------------------
        Int : the register entry associated with the Membre-Certificat pair
        String : User-friendly message that can be displayed
        """
        a = self.registre[membre, certificat]
        if a == Registre.NonCertifie:
            msg = f"{membre.prenom} n'a pas le certificat {certificat.nom}"
        elif a == Registre.CertificatPerdu:
            msg = f"{membre.prenom} n'a plus le certificat {certificat.nom}"
        elif a == Registre.Certificateur:
            msg = f"{membre.prenom} est certificateur\xb7rice pour le certificat {certificat.nom}"
        elif a >= Registre.Certifie:
            msg = f"{membre.prenom} a le certificat {certificat.nom}."
        else:
            msg = "Register internal error"

        return a, msg


    # The following methods allow to find a Membre or Certificat object
    # from string data (usually provided by the user)
    def find_membre_by_id(self, identification):
        for m in self.membres:
            if m.id == identification:
                return m
        return False

    def find_membre_by_name(self, prenom, nom):
        for m in self.membres:
            if m.prenom == prenom and m.nom == nom:
                return m
        return False

    def find_certificat_by_name(self, nom):
        for c in self.certificats:
            if c.nom == nom:
                return c
        return False

    def get_certificats(self, categorie):
        """Returns the list of Certificat objects for the given category"""
        return [c for c in self.certificats if c.categorie == categorie]

    def trier_membres(self, order="id"):
        if order == "id":
            self.membres.sort(key=lambda m: m.id.lower())
        elif order == "id_rev":
            self.membres.sort(key=lambda m: m.id.lower(), reverse=True)
        else:
            raise NotImplemented

    def trier_certificats(self):
        self.certificats.sort(key=lambda c: c.nom.lower())


    def enregistrer(self, file="registre_certificats.json"):
        """Stores the register in a local file in JSON format"""
        self.trier_membres("id")
        self.trier_certificats()
        jsonable = {}
        jsonable["membres"] = []
        for m in self.membres:
            jsonable["membres"].append((m.prenom, m.nom, m.id))

        jsonable["certificats"] = []
        for c in self.certificats:
            jsonable["certificats"].append((c.nom, c.categorie))

        jsonable["registre"] = {}
        for m in self.membres:
            jsonable["registre"][m.id] = []
            for c in self.certificats:
                jsonable["registre"][m.id].append((c.nom, self.registre[m, c]))

        with open(file, "w") as reg_file:
            json.dump(jsonable, reg_file)
            reg_file.close()

    def charger(self, file="registre_certificats.json", merge=False):
        """Loads a register from local JSON file into the Registre object"""
        try:
            if not merge: self.clear()
            with open(file, "r") as reg_file:
                reg_cert = json.load(reg_file)
                for m in reg_cert["membres"]:
                    self.ajouter_membre(m[0], m[1])

                for c in reg_cert["certificats"]:
                    self.ajouter_certificat(c[0], c[1])

                for mid in reg_cert["registre"]:
                    m = self.find_membre_by_id(mid)
                    for r in reg_cert["registre"][mid]:
                        c = self.find_certificat_by_name(r[0])
                        self.decerner_certificat(m, c, int(r[1]))
                self.trier_membres()
                self.trier_certificats()
        except FileNotFoundError:
            print("file does not exist")
            self = Registre()
        except Exception:
            return False


    def clear(self):
        """Erase all data"""
        self.membres = []
        self.certificats = []
        self.registre = {}
        self.categories = {}

    def __repr__(self):
        if not (self.membres or self.certificats):
            return "Le registre est vide"
        s = "\t"
        for c in self.certificats:
            s += c.nom[:7] + "\t"
        s += "\n"
        for m in self.membres:
            s += m.prenom[:7] + "\t"
            for c in self.certificats:
                s += str(self.registre[m, c]) + "\t"
            s += "\n"

        s += "\n"
        return s



def unambiguous_id(duplicates):
    """
    Ensures members ids are unique throughout the register

    Parameters
    ----------
    duplicates: list of Membre objects
        members that have the same prenom attribute
    """
    old_ids = [n.id for n in duplicates]
    for n in duplicates:
        n.id = n.prenom + " "
    i = 0
    ambiguous = True
    while ambiguous:
        ambiguous = False

        to_remove = []
        for n1 in duplicates:
            remove = True
            for n2 in duplicates:
                if n1.id == n2.id and n1 is not n2:
                    remove = False
                    ambiguous = True
            if remove:
                if i < len(n1.nom):
                    n1.id += "."
                to_remove.append(n1)

        for n in to_remove:
            duplicates.remove(n)

        to_remove = []
        for n in duplicates:
            if i >= len(n.nom):
                to_remove.append(n)

        for n in to_remove:
            duplicates.remove(n)

        for n in duplicates:
            n.id += n.nom[i]
        i += 1

    for n, old_id in zip(duplicates, old_ids):
        if i < len(n.nom):
            n.id += "."
        if len(n.id) < len(old_id):
            n.id = old_id

    # keeping ids shorter than 15 characters for printing
    for n in duplicates:
        i = n.id.find(' ') if ' ' in n.id else len(n.id)-1
        while len(n.id) > 15 and i > 1:
            n.id = n.id[:i] + n.id[i+1:]
            i -= 1

        # this happens in the rare case of 2 people having the same first
        # name and same first 13 last name letters.
        if len(n.id) > 15:
            raise ValueError("There are names that are way too long and too similar")

