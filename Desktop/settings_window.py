# coding: utf-8
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QCommandLinkButton, QSizePolicy
from PyQt5.QtCore import Qt, QItemSelectionModel, QThread
from widgets import *
from new_school_window import NewSchoolWindow
import cloud_support
import multithreading
import time
import language_selector as ls


class SettingsWindow(QMainWindow):
    """Provides UI to edit the register (member and certificate list)
       This window also serves as first screen for when there is no register
       loaded yet, in which case it displays a prompt to create/load a
       register"""
    def __init__(self, parent):
        super(SettingsWindow, self).__init__(parent)
        self.thread_running_flag = False
        self.setWindowModality(Qt.WindowModal)  # freeze parent window
        self.registre = self.parentWidget().registre
        self.school_name = self.parentWidget().school_name

        self.lay_out()

    def lay_out(self):
        self.setWindowTitle(ls.strings.PARAMETERS_BUTTON)
        self.layout = QVBoxLayout()

        # -----------  Callback functions  ----------
        def valider_callback():
            p = prenom.text()
            n = nom.text()
            if not p or not n:
                return
            err = self.registre.ajouter_membre(p, n)
            if type(err) == str:
                dialog(err, ls.strings.ERROR)
                return
            for _ in range(liste_membres.count()):
                liste_membres.takeItem(0)

            for m in self.registre.membres:
                liste_membres.addItem(m.id)
            self.update_registre()

        def retirer_membre_callback():
            if liste_membres.currentItem() is None:
                return
            identification = liste_membres.currentItem().text()
            m = self.registre.find_membre_by_id(identification)
            self.registre.supprimer_membre(m)
            for _ in range(liste_membres.count()):
                liste_membres.takeItem(0)
            for m in self.registre.membres:
                liste_membres.addItem(m.id)
            self.update_registre()

        def cat_list_connect(x, y):
            if x is not None:
                for cat in cert_lists:
                    cert_lists[cat].hide()
                cert_lists[x.text()].show()
                cert_label.setText(ls.strings.X_CAT_CERTIFICATES(x.text()))
            else:
                cat_input.setCurrentIndex(-1)

        def cat_input_connect(x):
            l = cat_list.findItems(x, Qt.MatchExactly)
            if l:
                cat_list.setCurrentItem(l[0])
                for cat in cert_lists:
                    cert_lists[cat].hide()
                cert_lists[x].show()

        def valider_cert_callback():
            cat = cat_input.currentText()
            nom = nom_input.text()
            if not cat or not nom:
                dialog(ls.strings.PLEASE_ENTER_CERTIFICATE_NAME_AND_CATEGORY)
                return
            err = self.registre.ajouter_certificat(nom, cat)
            if err is not None:
                dialog(err, ls.strings.ERROR)
                return
            if cat not in cert_lists:
                cert_lists[cat] = ResizableListWidget()
                b_left_layout.addWidget(cert_lists[cat])
                cert_lists[cat].hide()
            else:
                for _ in range(cert_lists[cat].count()):
                    cert_lists[cat].takeItem(0)
            for _ in range(cat_list.count()):
                cat_list.takeItem(0)
                cat_input.removeItem(0)
            for categ in self.registre.categories:
                cat_list.addItem(categ)
                cat_input.addItem(categ)
            if cat in self.registre.categories:
                for c in self.registre.get_certificats(cat):
                    cert_lists[cat].addItem(c.nom)

            cat_list.setCurrentItem(cat_list.findItems(cat, Qt.MatchExactly)[0])
            cat_input.setCurrentText(cat)

            cert_lists[cat].show()
            self.update_registre()

        def supprimer_certificat(nom, cat):
            c_row = cert_lists[cat].row(cert_lists[cat].currentItem())
            cert_lists[cat].takeItem(c_row)
            self.registre.supprimer_certificat(self.registre.find_certificat_by_name(nom))

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
            if confirm(ls.strings.DELETE_CATEGORY_Q):
                if cat_list.currentItem() is None:
                    return
                cat = cat_list.currentItem().text()
                for nom in [c.nom for c in self.registre.get_certificats(cat)]:
                    supprimer_certificat(nom, cat)
                cat_row = cat_list.row(cat_list.currentItem())
                cat_list.takeItem(cat_row)
                self.registre.supprimer_categorie(cat)
                cert_lists[cat].hide()
                self.update_registre()

        def avance_callback():
            if self.avance.text() == ls.strings.ADVANCED:
                self.avance.setText(ls.strings.HIDE)
                self.avance_w.show()
            else:
                self.avance.setText(ls.strings.ADVANCED)
                self.avance_w.hide()

        def change_school_callback():
            self.hide()
            NewSchoolWindow(self).show()

        def supprimer_registre_callback():
            if cloud_support.supprimer_registre(self.school_name):
                self.parentWidget().school_name = ""
                self.school_name = ""
                self.registre.clear()
            self.hide_widgets()

        def change_language_callback():
            ls.select_language(ls.strings.code)
            self.lay_out()
            self.parentWidget().lay_out()

        # --------------------------------------------------

        # header : create/load/delete online register buttons
        f = 20  # font size
        header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 0, 16, 0)
        self.school_name_w = QLabel(self.school_name)
        self.school_name_w.setFont(QFont("unknown", f))
        self.school_name_w.setMaximumHeight(60)
        self.avance = QCommandLinkButton(ls.strings.ADVANCED)
        self.avance.setMaximumWidth(100)
        self.avance_w = QWidget()
        if self.school_name != "": self.avance_w.hide()
        avance_layout = QHBoxLayout()
        avance_layout.setContentsMargins(0, 0, 0, 0)
        self.avance_w.setLayout(avance_layout)
        self.change_school = QPushButton(ls.strings.CREATE_LOAD_REGISTER)
        self.supprimer_registre = QPushButton(ls.strings.DELETE_REGISTER)
        self.supprimer_registre.setMaximumWidth(300)
        avance_layout.addWidget(self.change_school)
        avance_layout.addWidget(self.supprimer_registre)
        header_layout.addWidget(self.school_name_w)
        header_layout.addWidget(self.avance)
        header_layout.addWidget(self.avance_w)
        header.setLayout(header_layout)
        self.layout.addWidget(header)

        self.avance.clicked.connect(avance_callback)
        self.change_school.clicked.connect(change_school_callback)
        self.supprimer_registre.clicked.connect(supprimer_registre_callback)

        # top widget : member list management
        self.gestion_membres = QWidget()
        self.gestion_membres.setMaximumHeight(300)
        membres_layout = QHBoxLayout()
        t_left_w = QWidget()
        t_right_w = QWidget()
        t_left_layout = QVBoxLayout()
        t_right_layout = QVBoxLayout()
        t_left_w.setLayout(t_left_layout)
        t_right_w.setLayout(t_right_layout)
        liste_membres_label = QLabel(ls.strings.MEMBER_LIST)
        ajouter_membre = QLabel(ls.strings.ADD_MEMBER)
        prenom = MyLineEdit(placeholder=ls.strings.FIRST_NAME)
        nom = MyLineEdit(placeholder=ls.strings.LAST_NAME)
        prenom.setFont(QFont("unknown", 15))
        nom.setFont(QFont("unknown", 15))
        liste_membres = ResizableListWidget()
        for m in self.registre.membres:
            liste_membres.addItem(m.id)
        valider = ResizableButton(ls.strings.VALIDATE)
        retirer_membre = ResizableButton(ls.strings.REMOVE_MEMBER)
        t_left_layout.addWidget(liste_membres_label)
        t_left_layout.addWidget(liste_membres)
        t_left_layout.addWidget(retirer_membre)
        t_right_layout.addWidget(ajouter_membre)
        t_right_layout.addWidget(prenom)
        t_right_layout.addWidget(nom)
        t_right_layout.addWidget(valider)
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
        cat_label = QLabel(ls.strings.CATEGORIES)
        cat_list = ResizableListWidget()
        cat_list.addItems(self.registre.categories)
        cert_label = QLabel(ls.strings.CERTIFICATES)
        ajouter_certificat = QLabel(ls.strings.ADD_CERTIFICATE)
        cat_input = MyComboBox(placeholder=ls.strings.CATEGORY)
        cat_input.setFont(QFont("unknown", 15))
        cat_input.addItems(self.registre.categories)
        valider_cert = ResizableButton(ls.strings.VALIDATE)
        nom_input = MyLineEdit(placeholder=ls.strings.CERTIFICATE_NAME)
        nom_input.setFont(QFont("unknown", 15))
        supprs_w = QWidget()
        supprs_layout = QHBoxLayout()
        suppr_cert = ResizableButton(ls.strings.DELETE_CERTIFICATE)
        suppr_cat = ResizableButton(ls.strings.DELETE_CATEGORY)
        supprs_w.setLayout(supprs_layout)
        self.gestion_certificats.setLayout(certificats_layout)
        b_left_layout.addWidget(cat_label)
        b_left_layout.addWidget(cat_list)
        b_left_layout.addWidget(cert_label)
        cert_lists = {}
        for cat in self.registre.categories:
            cert_lists[cat] = ResizableListWidget()
            for cert in self.registre.get_certificats(cat):
                cert_lists[cat].addItem(cert.nom)
            b_left_layout.addWidget(cert_lists[cat])
            cert_lists[cat].hide()
        b_right_layout.addWidget(ajouter_certificat)
        b_right_layout.addWidget(cat_input)
        b_right_layout.addWidget(nom_input)
        b_right_layout.addWidget(valider_cert)
        supprs_layout.addWidget(suppr_cert)
        supprs_layout.addWidget(suppr_cat)
        b_right_layout.addWidget(supprs_w)
        certificats_layout.addWidget(b_left_w)
        certificats_layout.addWidget(b_right_w)

        # footer
        self.footer = QWidget()
        footer_layout = QHBoxLayout()
        change_language = QPushButton(ls.strings.LANGUAGE + ls.strings.name)
        change_language.setMaximumWidth(change_language.sizeHint().width())
        self.thread_progress = QLabel(ls.strings.SAVED)
        self.thread_progress.setAlignment(Qt.AlignRight)
        self.thread_progress.setStyleSheet("color:grey")
        footer_layout.addWidget(change_language)
        footer_layout.addWidget(self.thread_progress)
        self.footer.setLayout(footer_layout)

        self.layout.addWidget(self.gestion_membres)
        self.layout.addWidget(self.gestion_certificats)
        self.layout.addWidget(self.footer)
        main_widget = QWidget()
        main_widget.setLayout(self.layout)
        self.setCentralWidget(main_widget)
        self.hide_widgets()

        # connecting slots
        valider.clicked.connect(valider_callback)
        retirer_membre.clicked.connect(retirer_membre_callback)
        cat_list.currentItemChanged.connect(cat_list_connect)
        cat_input.currentTextChanged.connect(cat_input_connect)
        valider_cert.clicked.connect(valider_cert_callback)
        suppr_cert.clicked.connect(suppr_cert_callback)
        suppr_cat.clicked.connect(suppr_cat_callback)
        change_language.clicked.connect(change_language_callback)

        cat_list.setCurrentRow(0, QItemSelectionModel.Select)

    def update_registre(self):
        self.parentWidget().registre_updated_flag = True
        self.registre.enregistrer()
        self.upload_in_thread()

    def hide_widgets(self):
        if self.school_name:
            self.school_name_w.setText(self.school_name)
            self.gestion_membres.show()
            self.gestion_certificats.show()
            self.supprimer_registre.show()
            self.avance.show()
            self.thread_progress.show()
            self.resize(710, 600)
        else:
            self.school_name_w.setText(ls.strings.CLICK_HERE_TO_BEGIN)
            self.gestion_membres.hide()
            self.gestion_certificats.hide()
            self.change_school.show()
            self.supprimer_registre.hide()
            self.avance.hide()
            self.thread_progress.hide()
            self.resize(710, 60)

    def closeEvent(self, event):
        self.parentWidget().update_comboboxes()
        self.parentWidget().setWindowOpacity(1.)
        super(SettingsWindow, self).closeEvent(event)

    def close_avance(self):
        self.avance.setText(ls.strings.ADVANCED)
        self.avance_w.hide()

    def upload_in_thread(self):
        if self.thread_running_flag:
            return
        else:
            self.thread_running_flag = True
        self.thread = QThread()
        self.uploader = multithreading.Uploader()
        self.uploader.moveToThread(self.thread)
        self.thread.started.connect(self.uploader.run)
        self.uploader.finished.connect(self.thread.quit)
        self.uploader.finished.connect(self.uploader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def finished():
            self.thread_progress.setText(ls.strings.SAVED)
            self.thread_running_flag = False

        def started():
            self.thread_progress.setText(ls.strings.SAVING)

        self.uploader.finished.connect(finished)
        self.uploader.started.connect(started)

        self.thread.start()

