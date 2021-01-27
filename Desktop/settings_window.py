# coding: utf-8

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from widgets import *
from new_school_window import NewSchoolWindow
import cloud_support
from multithreading import Uploader

# TODO: update function that uploads registre (and label at bottom right)

def show_new_school(parent):
    NewSchoolWindow(parent).show()


class SettingsWindow(QMainWindow):
    def __init__(self, parent, registre):
        super(SettingsWindow, self).__init__(parent)

        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("Paramètres")
        self.registre = registre

        self.layout = QVBoxLayout()

        # header : gestion du compte d'école
        header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 0, 16, 0)

        f = 20
        sn = self.parentWidget().school_name
        s = sn if sn != "" else "Cliquez ici pour commencer : "


        self.school_name_w = QLabel(s)
        self.school_name_w.setFont(QFont("unknown", f))
        self.school_name_w.setMaximumHeight(60)
        header_layout.addWidget(self.school_name_w)


        self.avance = QCommandLinkButton("Avancé")
        self.avance.clicked.connect(self.avance_callback)
        self.avance.setMaximumWidth(100)
        header_layout.addWidget(self.avance)

        self.avance_w = QWidget()
        if self.parentWidget().school_name != "":
            self.avance_w.hide()
        header_layout.addWidget(self.avance_w)

        avance_layout = QHBoxLayout()
        avance_layout.setContentsMargins(0, 0, 0, 0)
        self.avance_w.setLayout(avance_layout)


        self.change_school = QPushButton("Créer/Charger registre")
        self.change_school.clicked.connect(lambda x: show_new_school(self))

        self.supprimer_registre = QPushButton("Supprimer registre")
        self.supprimer_registre.clicked.connect(self.supprimer_registre_callback)
        self.supprimer_registre.setMaximumWidth(300)


        avance_layout.addWidget(self.change_school)
        avance_layout.addWidget(self.supprimer_registre)

        header.setLayout(header_layout)

        self.layout.addWidget(header)

        # top widget : gestion des membres
        self.gestion_membres = QWidget()
        self.gestion_membres.setMaximumHeight(300)
        membres_layout = QHBoxLayout()

        t_left_w = QWidget()
        t_right_w = QWidget()

        t_left_layout = QVBoxLayout()
        t_right_layout = QVBoxLayout()

        t_left_w.setLayout(t_left_layout)
        t_right_w.setLayout(t_right_layout)

        liste_membres_label = QLabel("Liste des membres :")
        t_left_layout.addWidget(liste_membres_label)

        ajouter_membre = QLabel("Ajouter membre :")
        t_right_layout.addWidget(ajouter_membre)

        prenom = MyLineEdit(placeholder="Prénom")
        nom = MyLineEdit(placeholder="Nom")

        prenom.setFont(QFont("unknown", 15))
        nom.setFont(QFont("unknown", 15))

        t_right_layout.addWidget(prenom)
        t_right_layout.addWidget(nom)

        valider = ResizableButton("Valider")

        def valider_callback():
            p = prenom.text()
            n = nom.text()
            if not p or not n:
                return
            registre.ajouter_membre(p, n)
            for _ in range(liste_membres.count()):
                liste_membres.takeItem(0)

            for m in registre.membres:
                liste_membres.addItem(m.id)
            self.update_registre()

        valider.clicked.connect(valider_callback)
        t_right_layout.addWidget(valider)

        liste_membres = ResizableListWidget()

        for m in registre.membres:
            liste_membres.addItem(m.id)

        t_left_layout.addWidget(liste_membres)

        def retirer_membre_callback():
            if liste_membres.currentItem() is None:
                return
            identification = liste_membres.currentItem().text()
            m = registre.find_membre_by_id(identification)
            registre.supprimer_membre(m)

            for _ in range(liste_membres.count()):
                liste_membres.takeItem(0)

            for m in registre.membres:
                liste_membres.addItem(m.id)

            self.update_registre()

        retirer_membre = ResizableButton("Retirer le membre")
        retirer_membre.clicked.connect(retirer_membre_callback)
        t_left_layout.addWidget(retirer_membre)

        membres_layout.addWidget(t_left_w)
        membres_layout.addWidget(t_right_w)
        self.gestion_membres.setLayout(membres_layout)


        # bottom widget : gestion des certificats
        self.gestion_certificats = QWidget()
        certificats_layout = QHBoxLayout()

        b_left_w = QWidget()
        b_right_w = QWidget()

        b_left_layout = QVBoxLayout()
        b_right_layout = QVBoxLayout()

        b_left_w.setLayout(b_left_layout)
        b_right_w.setLayout(b_right_layout)

        cat_label = QLabel("Catégories :")
        b_left_layout.addWidget(cat_label)

        cat_list = ResizableListWidget()
        b_left_layout.addWidget(cat_list)

        cert_label = QLabel("Certificats :")
        b_left_layout.addWidget(cert_label)

        cert_lists = {}
        for cat in registre.categories:
            cat_list.addItem(cat)
            cert_lists[cat] = ResizableListWidget()
            for cert in registre.get_certificats(cat):
                cert_lists[cat].addItem(cert.nom)
            b_left_layout.addWidget(cert_lists[cat])
            cert_lists[cat].hide()


        ajouter_certificat = QLabel("Ajouter certificat :")
        b_right_layout.addWidget(ajouter_certificat)

        cat_input = MyComboBox(placeholder="Catégorie")
        cat_input.setFont(QFont("unknown", 15))
        cat_input.addItems(registre.categories)

        def cat_list_connect(x, y):
            if x is not None:
                # cat_input.setCurrentText(x.text())
                for cat in cert_lists:
                    cert_lists[cat].hide()
                cert_lists[x.text()].show()
                cert_label.setText(f"Certificats {x.text()} :")
            else:
                cat_input.setCurrentIndex(-1)

        cat_list.currentItemChanged.connect(cat_list_connect)

        def cat_input_connect(x):
            l = cat_list.findItems(x, Qt.MatchExactly)
            if l:
                cat_list.setCurrentItem(l[0])
                for cat in cert_lists:
                    cert_lists[cat].hide()
                cert_lists[x].show()

        cat_input.currentTextChanged.connect(cat_input_connect)
        cat_list.setCurrentRow(0, QItemSelectionModel.Select)

        nom_input = MyLineEdit(placeholder="Nom du certificat")
        nom_input.setFont(QFont("unknown", 15))

        b_right_layout.addWidget(cat_input)
        b_right_layout.addWidget(nom_input)

        valider_cert = ResizableButton("Valider")
        b_right_layout.addWidget(valider_cert)

        def valider_cert_callback():
            cat = cat_input.currentText()
            nom = nom_input.text()
            if not cat or not nom:
                return

            if cat not in registre.categories:
                cert_lists[cat] = ResizableListWidget()
                b_left_layout.addWidget(cert_lists[cat])
                cert_lists[cat].hide()
            else:
                for _ in range(cert_lists[cat].count()):
                    cert_lists[cat].takeItem(0)

            registre.ajouter_certificat(nom, cat)

            for _ in range(cat_list.count()):
                cat_list.takeItem(0)
                cat_input.removeItem(0)

            for categ in registre.categories:
                cat_list.addItem(categ)
                cat_input.addItem(categ)

            for c in registre.get_certificats(cat):
                cert_lists[cat].addItem(c.nom)

            cat_list.setCurrentItem(cat_list.findItems(cat, Qt.MatchExactly)[0])
            cat_input.setCurrentText(cat)

            cert_lists[cat].show()
            self.parentWidget().create_cert_box(nom, cat)
            self.update_registre()


        valider_cert.clicked.connect(valider_cert_callback)


        supprs_w = QWidget()
        supprs_layout = QHBoxLayout()

        suppr_cert = ResizableButton("Supprimer Certificat")
        supprs_layout.addWidget(suppr_cert)

        def supprimer_certificat(nom, cat):
            c_row = cert_lists[cat].row(cert_lists[cat].currentItem())
            cert_lists[cat].takeItem(c_row)
            registre.supprimer_certificat(registre.find_certificat_by_name(nom))


        def suppr_cert_callback():
            cat = cat_list.currentItem()
            nom = cert_lists[cat.text()].currentItem()
            if nom is None or cat is None:
                return
            nom = nom.text()
            cat = cat.text()

            supprimer_certificat(nom, cat)
            self.update_registre()

        def suppr_cat_callback():
            if confirm("Supprimer Catégorie ?"):
                cat = cat_list.currentItem().text()
                for nom in [c.nom for c in registre.get_certificats(cat)]:
                    supprimer_certificat(nom, cat)
                cat_row = cat_list.row(cat_list.currentItem())
                cat_list.takeItem(cat_row)
                registre.supprimer_categorie(cat)
                cert_lists[cat].hide()
                self.update_registre()


        suppr_cert.clicked.connect(suppr_cert_callback)

        suppr_cat = ResizableButton("Supprimer Catégorie")
        supprs_layout.addWidget(suppr_cat)

        suppr_cat.clicked.connect(suppr_cat_callback)

        supprs_w.setLayout(supprs_layout)
        b_right_layout.addWidget(supprs_w)

        certificats_layout.addWidget(b_left_w)
        certificats_layout.addWidget(b_right_w)

        self.gestion_certificats.setLayout(certificats_layout)

        self.thread_progress = QLabel("Enregistré")
        self.thread_progress.setAlignment(Qt.AlignRight)
        self.thread_progress.setStyleSheet("color:grey")



        self.layout.addWidget(self.gestion_membres)
        self.layout.addWidget(self.gestion_certificats)
        self.layout.addWidget(self.thread_progress)

        self.hide_widgets()

        main_widget = QWidget()
        main_widget.setLayout(self.layout)

        self.setCentralWidget(main_widget)

        if self.parentWidget().school_name != "":
            self.resize(710, 600)
        else:
            self.resize(710, 60)

    def update_registre(self):
        self.parentWidget().registre_updated_flag = True
        self.registre.enregistrer()
        self.upload_in_thread(self.thread_progress)

    def hide_widgets(self):
        if self.parentWidget().school_name != "":
            self.school_name_w.setText(self.parentWidget().school_name)
            self.gestion_membres.show()
            self.gestion_certificats.show()
            self.supprimer_registre.show()
            self.avance.show()
            self.resize(710, 600)
        else:
            self.school_name_w.setText("Cliquez ici pour commencer : ")
            self.gestion_membres.hide()
            self.gestion_certificats.hide()
            self.supprimer_registre.hide()
            self.avance.hide()
            self.resize(710, 60)


    def closeEvent(self, event):
        super(SettingsWindow, self).closeEvent(event)
        self.parentWidget().update_comboboxes()


    def supprimer_registre_callback(self):
        if cloud_support.supprimer_registre(self.parentWidget().school_name):
            self.parentWidget().school_name = ""
            self.registre.clear()
        self.hide_widgets()

    def avance_callback(self, x):
        if self.avance.text() == "Avancé":
            self.avance.setText("Masquer")
            self.avance_w.show()
        else:
            self.avance.setText("Avancé")
            self.avance_w.hide()

    def close_avance(self):
        self.avance.setText("Avancé")
        self.avance_w.hide()

    def upload_in_thread(self, w):
        self.thread = QThread()
        self.uploader = Uploader()
        self.uploader.moveToThread(self.thread)
        self.thread.started.connect(self.uploader.run)
        self.uploader.finished.connect(self.thread.quit)
        self.uploader.finished.connect(self.uploader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.uploader.finished.connect(
            lambda: w.setText("Enregistré")
        )
        self.uploader.started.connect(
            lambda: w.setText("Enregistrement...")
        )

        self.thread.start()

