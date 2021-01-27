# coding: utf-8
import os
import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from widgets import *
from registre_manager import Registre
import excel
from settings_window import SettingsWindow
from multithreading import Uploader
import cloud_support

import sys


def show_settings(parent, registre):
    settings_window = SettingsWindow(parent, registre)
    settings_window.show()

class MainWindow(QMainWindow):
    def __init__(self, registre=None):
        super(MainWindow, self).__init__()
        if registre is None:
            print("registre is None")
            return 1
        self.registre_updated_flag = False


        self.setWindowTitle("Registre des certificats")


        self.layout = QVBoxLayout()

        self.title = QLabel("Registre des certificats")
        self.title.setFont(QFont("unknown", 13))
        self.title.setAlignment(Qt.AlignCenter)

        self.param_imprim = QWidget()
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        self.parametres = QPushButton("Paramètres")
        self.parametres.clicked.connect(lambda x: show_settings(self, registre))
        self.imprimer = QPushButton("Imprimer")
        self.imprimer.clicked.connect(self.imprimer_callback)

        self.h_layout.addWidget(self.parametres)
        self.h_layout.addWidget(self.imprimer)
        self.param_imprim.setLayout(self.h_layout)

        self.membres = MyComboBox(placeholder="Membre")
        self.membres.setFont(QFont("unknown", 13))
        self.membres.addItems([m.id for m in registre.membres])
        self.membres.currentTextChanged.connect(self.update)

        self.categories = MyComboBox(placeholder="Catégorie")
        self.categories.setFont(QFont("unknown", 13))
        self.categories.addItems([c for c in registre.categories])
        self.categories.currentTextChanged.connect(self.update)

        self.cert_boxes = {}
        for c in registre.categories:
            self.cert_boxes[c] = MyComboBox(placeholder="Certificat")
            self.cert_boxes[c].setFont(QFont("unknown", 13))
            self.cert_boxes[c].addItems([c.nom for c in registre.get_certificats(c)])
            self.cert_boxes[c].currentTextChanged.connect(self.update)

        self.status = QLabel()
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setFont(QFont("unknown", 12))


        self.decerner = QPushButton("Décerner certificat")

        self.rendre_certificateur = QPushButton("Nouveau Certificateur")

        self.thread_progress = QLabel("Enregistré")
        self.thread_progress.setAlignment(Qt.AlignRight)
        self.thread_progress.setStyleSheet("color:grey")


        # erase certificate text when theres a new category entry 
        # (!dirty pythonic trick used, see get() doc)
        self.categories.currentTextChanged.connect(lambda x: self.cert_boxes.get(\
            self.categories.currentText(), MyComboBox()).setCurrentIndex(-1))

        self.decerner.clicked.connect(self.decerner_callback)
        self.rendre_certificateur.clicked.connect(self.rendre_certificateur_callback)

        # organizing widgets
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.param_imprim)
        self.layout.addWidget(self.membres)
        self.layout.addWidget(self.categories)

        for c in registre.categories:
            self.layout.addWidget(self.cert_boxes[c])
            self.cert_boxes[c].hide()

        self.layout.addWidget(self.status)
        self.layout.addWidget(self.decerner)
        self.layout.addWidget(self.rendre_certificateur)
        self.layout.addWidget(self.thread_progress)

        self.decerner.hide()
        self.rendre_certificateur.hide()

        widget = QWidget()
        widget.setLayout(self.layout)


        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)
        self.resize(self.layout.sizeHint())

        if os.path.exists("school_name.txt"):
            with open("school_name.txt", "r") as f:
                self.school_name = f.read()
        else:
            self.school_name = ""

        if self.school_name == "":
            show_settings(self, registre)


    def update(self):
        print(self.school_name, self.registre_updated_flag)
        if self.school_name != "" and self.registre_updated_flag:
            registre.enregistrer()
            self.upload_in_thread(self.thread_progress)

        self.registre_updated_flag = False
        self.show_cert_boxes()
        membre = self.membres.currentText()
        certificat = self.cert_boxes.get(self.categories.currentText(), MyComboBox()).currentText()

        m = registre.find_membre_by_id(membre)
        c = registre.find_certificat_by_name(certificat)

        if not (m and c):
            self.status.setText("")
            self.rendre_certificateur.hide()
            self.decerner.hide()
        else:
            self.status.setText(registre.a_le_certificat(m, c)[1])

            a = registre.a_le_certificat(m, c)[0]
            if a == Registre.Certifie:
                self.decerner.setText("Retirer certificat")
                self.decerner.show()
                self.rendre_certificateur.show()
            elif a == Registre.Certificateur:
                self.decerner.setText("Retirer certificat")
                self.decerner.show()
                self.rendre_certificateur.hide()
            elif a == Registre.NonCertifie or a == Registre.CertificatPerdu:
                self.decerner.setText("Décerner certificat")
                self.decerner.show()
                self.rendre_certificateur.hide()

        self.resize(QSize(max(self.layout.sizeHint().width(), self.width()),
                          max(self.layout.sizeHint().height(), self.height())))


    def update_comboboxes(self):
        for i in range(self.membres.count()):
            self.membres.removeItem(0)

        self.membres.addItems([m.id for m in registre.membres])

        for _ in range(self.categories.count()):
            self.categories.removeItem(0)
        for cat in registre.categories:
            self.categories.addItems([cat])
            for _ in range(self.cert_boxes[cat].count()):
                self.cert_boxes[cat].removeItem(0)

            self.cert_boxes[cat].addItems([c.nom for c in registre.get_certificats(cat)])
            self.cert_boxes[cat].hide()
        self.resize(self.layout.sizeHint())



    def decerner_callback(self):
        membre = self.membres.currentText()
        certificat = self.cert_boxes.get(self.categories.currentText(), MyComboBox()).currentText()

        m = registre.find_membre_by_id(membre)
        c = registre.find_certificat_by_name(certificat)
        if not (m and c):
            return
        else:
            if self.decerner.text() == "Retirer certificat":
                if not confirm(f"Retirer le certificat {c.nom} à {m.id} ?"):
                     return
                registre.decerner_certificat(m, c, registre.CertificatPerdu)
                self.rendre_certificateur.hide()
            elif self.decerner.text() == "Décerner certificat":
                if not confirm(f"Décerner le certificat {c.nom} à {m.id} ?"):
                     return
                registre.decerner_certificat(m, c, registre.Certifie)
                self.rendre_certificateur.show()

            self.registre_updated_flag = True
            self.update()


    def rendre_certificateur_callback(self):
        membre = self.membres.currentText()
        certificat = self.cert_boxes.get(self.categories.currentText(), MyComboBox()).currentText()

        m = registre.find_membre_by_id(membre)
        c = registre.find_certificat_by_name(certificat)
        self.rendre_certificateur.hide()
        if not (m and c):
            return
        else:
            if not confirm(f"Rendre {m.id} certificateur\xb7rice pour le certificat {c.nom} ?"):
                return
            registre.decerner_certificat(m, c, registre.Certificateur)
            self.registre_updated_flag = True

        self.update()

    def imprimer_callback(self):
        excel.generer_registre(registre)

    def create_cert_box(self, nom, cat):
        if cat not in self.cert_boxes:
            self.cert_boxes[cat] = MyComboBox(placeholder="Certificat")
            self.cert_boxes[cat].addItem(nom)
            self.cert_boxes[cat].currentTextChanged.connect(self.update)
            self.layout.insertWidget(3, self.cert_boxes[cat])
            self.cert_boxes[cat].hide()
        elif nom not in [c.nom for c in registre.get_certificats(cat)]:
            self.cert_boxes[cat].addItem(nom)

    def show_cert_boxes(self):
        cat = self.categories.currentText()
        if cat not in registre.categories:
            return

        for c in registre.categories:
            self.cert_boxes[c].hide()

        if cat in registre.categories:
            self.cert_boxes[cat].show()

    def upload_in_thread(self, label):
        self.thread = QThread()
        self.uploader = Uploader()
        self.uploader.moveToThread(self.thread)
        self.thread.started.connect(self.uploader.run)
        self.uploader.finished.connect(self.thread.quit)
        self.uploader.finished.connect(self.uploader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.uploader.finished.connect(
            lambda: label.setText("Enregistré")
        )
        self.uploader.started.connect(
            lambda: label.setText("Enregistrement...")
        )

        self.thread.start()


app = QApplication(sys.argv)

registre = Registre()
print(registre)
registre.ajouter_membres([("Christelle", "Alaux"), ("Christelle", "Bergerac"), ("Christophe", "Maé"),
                          ("Marion", "Raynal"), ("Pierre", "Grangier"),
                          ("melissandre-emmanuel", "schmidt")])
registre.ajouter_certificats([("Guitare", "Musique"), ("Piano", "Musique"),
                               ("Sortie", "Extérieur"), ("Grimper aux arbres",
                                                          "Extérieur")])
registre.enregistrer()
print(registre)

# creating local ids file if it doesn't exist
if not os.path.exists("json_local_school_ids.json"):
    with open("json_local_school_ids.json", "w") as f:
        f.write("{}")

window = MainWindow(registre)
window.show()

app.exec_()

