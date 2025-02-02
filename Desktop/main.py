# coding: utf-8
import os
import time
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QCompleter
from PyQt5.QtCore import QThread, Qt

from registre_manager import Registre
import excel
from settings_window import SettingsWindow
import multithreading
import cloud_support
import language_selector as ls
from widgets import *

import sys


class MainUsage(QMainWindow):
    """Main window of the application, kept simple and designed
        to be used by people who award certificates."""
    def __init__(self):
        super(MainUsage, self).__init__()
        if not ls.load_language():
            ls.select_language("en")

        # continuously check connection in background
        self.check_connection_in_thread()

        # checking if a register has previously been loaded
        self.registre = Registre()  # empty register
        self.school_name = ""  # also serves as indicator that a register has been loaded
        if os.path.exists("school_name.txt") and os.path.exists("p.rc"):
            with open("school_name.txt", "r") as f:
                self.school_name = f.read()
            with open("p.rc") as f:
                p = f.read()
            try:
                # if local files exist, download from cloud
                if self.school_name \
                and cloud_support.download_registre(self.school_name, p):
                    self.registre = Registre()
                    self.registre.charger()
            except KeyError:
                self.school_name = ""
                open("school_name.txt", "w").close()

        # if no register is loaded, settings_window serves as first screen to 
        # guide user through creating/loading a new register
        if not self.school_name:
            self.show_settings()


        self.registre_updated_flag = False
        self.thread_running_flag = False

        self.lay_out()

    def lay_out(self):
        """lays out main window on initialization
            and connects button callbacks"""
        self.setWindowTitle(ls.strings.TITLE)
        self.layout = QVBoxLayout()
        self.title = QLabel(ls.strings.TITLE)
        self.title.setFont(QFont("unknown", 13))
        self.title.setAlignment(Qt.AlignCenter)
        self.param_imprim = QWidget()
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.parametres = QPushButton(ls.strings.PARAMETERS_BUTTON)
        self.imprimer = QPushButton(ls.strings.PRINT_BUTTON)
        self.h_layout.addWidget(self.parametres)
        self.h_layout.addWidget(self.imprimer)
        self.param_imprim.setLayout(self.h_layout)
        self.membres = MyComboBox(placeholder=ls.strings.MEMBER_CB)
        self.membres.setFont(QFont("unknown", 13))
        self.membres.addItems([m.id for m in self.registre.membres])
        self.categories = MyComboBox(placeholder=ls.strings.CATEG_CB)
        self.categories.setFont(QFont("unknown", 13))
        self.categories.addItems([c for c in self.registre.categories])
        self.cert_box = MyComboBox(placeholder=ls.strings.CERT_CB)
        self.cert_box.setFont(QFont("unknown", 13))
        self.status = QLabel()
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setFont(QFont("unknown", 12))
        self.decerner = QPushButton(ls.strings.AWARD_CERTIFICATE)
        self.rendre_certificateur = QPushButton(ls.strings.MAKE_CERTIFICATOR_BUTTON)
        self.reinitialiser = QPushButton(ls.strings.REINITIALIZE_BUTTON)
        self.thread_progress = QLabel(ls.strings.SAVED)
        self.thread_progress.setAlignment(Qt.AlignRight)
        self.thread_progress.setStyleSheet("color:grey")
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.param_imprim)
        self.layout.addWidget(self.membres)
        self.layout.addWidget(self.categories)
        self.layout.addWidget(self.cert_box)
        self.layout.addWidget(self.status)
        self.layout.addWidget(self.decerner)
        self.layout.addWidget(self.rendre_certificateur)
        self.layout.addWidget(self.reinitialiser)
        self.layout.addWidget(self.thread_progress)
        self.decerner.hide()
        self.rendre_certificateur.hide()
        self.reinitialiser.hide()
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.resize(self.layout.sizeHint())

        # -----------  connecting slots  ---------------

        self.parametres.clicked.connect(self.show_settings)
        self.imprimer.clicked.connect(self.imprimer_callback)
        self.decerner.clicked.connect(self.decerner_callback)
        self.rendre_certificateur.clicked.connect(self.rendre_certificateur_callback)
        self.reinitialiser.clicked.connect(self.reinitialiser_callback)
        self.membres.currentTextChanged.connect(self.update)
        self.categories.currentTextChanged.connect(self.update)
        self.cert_box.currentTextChanged.connect(self.update)


    def update(self):
        """Frequently called function that updates both register data and UI"""

        # ----------  updating register data ----------
        if not self.school_name:
            # first prompt screen if no school name
            self.show_settings()
        else:
            if self.registre_updated_flag:
                self.upload_in_thread()
            else:
                self.download_in_thread()
        self.registre_updated_flag = False

        # ---------------  updating UI  ---------------
        self.update_comboboxes()

        membre = self.membres.currentText()
        certificat = self.cert_box.currentText()

        m = self.registre.find_membre_by_id(membre)
        c = self.registre.find_certificat_by_name(certificat)

        if not m or not c:
            self.rendre_certificateur.hide()
            self.decerner.hide()
            self.reinitialiser.hide()

        if not m and not c:
            msg = ""
        elif m and not c:
            _, msg = self.registre.get_certificats_for_member(m)
        elif not m and c:
            _, msg = self.registre.get_members_for_certificat(c)
        else:
            a, msg = self.registre.a_le_certificat(m, c)

            if a == Registre.Certifie:
                self.decerner.setText(ls.strings.REVOKE_CERTIFICATE)
                self.decerner.show()
                self.rendre_certificateur.show()
                self.reinitialiser.hide()
            elif a == Registre.Certificateur:
                self.decerner.setText(ls.strings.REVOKE_CERTIFICATE)
                self.decerner.show()
                self.rendre_certificateur.hide()
                self.reinitialiser.hide()
            elif a == Registre.NonCertifie:
                self.decerner.setText(ls.strings.AWARD_CERTIFICATE)
                self.decerner.show()
                self.rendre_certificateur.hide()
                self.reinitialiser.hide()
            elif a == Registre.CertificatPerdu:
                self.decerner.setText(ls.strings.AWARD_CERTIFICATE)
                self.decerner.show()
                self.reinitialiser.show()
                self.rendre_certificateur.hide()


        self.status.setText(msg)
        self.resize(QSize(max(self.layout.sizeHint().width(), self.width()),
                          max(self.layout.sizeHint().height(), self.height())))


    def update_comboboxes(self):
        """Loads data from self.registre into the members and category
        widgets"""
        saved_text_m = self.membres.currentText()
        saved_text_cat = self.categories.currentText()
        saved_text_cert = self.cert_box.currentText()

        # prevent signals from retriggering self.update
        self.membres.currentTextChanged.disconnect(self.update)
        self.categories.currentTextChanged.disconnect(self.update)
        self.cert_box.currentTextChanged.disconnect(self.update)

        # deleting possibly obsolete data
        self.membres.clear()
        self.categories.clear()
        self.cert_box.clear()

        # filling in updated data
        self.membres.addItems([m.id for m in self.registre.membres])
        self.categories.addItems(self.registre.categories)
        if saved_text_cat in self.registre.categories:
            self.cert_box.addItems([c.nom for c in
                                    self.registre.get_certificats(saved_text_cat)])
        else:
            self.cert_box.addItems([c.nom for c in self.registre.certificats])

        # restoring saved text
        self.membres.setEditText(saved_text_m)
        self.categories.setEditText(saved_text_cat)
        self.cert_box.setEditText(saved_text_cert)

        # reconnecting slots
        self.membres.currentTextChanged.connect(self.update)
        self.categories.currentTextChanged.connect(self.update)
        self.cert_box.currentTextChanged.connect(self.update)

        self.resize(self.layout.sizeHint())

    def show_settings(self):
        self.setWindowOpacity(0.)
        settings_window = SettingsWindow(self)
        settings_window.show()

    def decerner_callback(self):
        """awards or removes a certificate to/from a member"""
        membre = self.membres.currentText()
        certificat = self.cert_box.currentText()

        m = self.registre.find_membre_by_id(membre)
        c = self.registre.find_certificat_by_name(certificat)
        if not m or not c:
            return
        else:
            if self.decerner.text() == ls.strings.REVOKE_CERTIFICATE:
                if not confirm(ls.strings.REMOVE_CERTIFICATE_FROM(m.id, c.nom)):
                     return
                self.registre.decerner_certificat(m, c, self.registre.CertificatPerdu)
                self.rendre_certificateur.hide()
            elif self.decerner.text() == ls.strings.AWARD_CERTIFICATE:

                if not confirm(ls.strings.AWARD_CERTIFICATE_TO(m.id, c.nom)):
                     return
                self.registre.decerner_certificat(m, c, self.registre.Certifie)
                self.rendre_certificateur.show()

            self.registre_updated_flag = True
            self.update()


    def rendre_certificateur_callback(self):
        """ makes the person able to award the certificate
            to someone else """
        membre = self.membres.currentText()
        certificat = self.cert_box.currentText()

        m = self.registre.find_membre_by_id(membre)
        c = self.registre.find_certificat_by_name(certificat)
        if not (m and c):
            return
        else:
            if not confirm(ls.strings.MAKE_CERTIFICATOR(m.id, c.nom)):
                return
            self.rendre_certificateur.hide()
            self.registre.decerner_certificat(m, c, self.registre.Certificateur)
            self.registre_updated_flag = True
            self.update()

    def reinitialiser_callback(self):
        """ Erase the history of a person who has lost a certificate (as if
        they just never had the certificate) """
        membre = self.membres.currentText()
        certificat = self.cert_box.currentText()

        m = self.registre.find_membre_by_id(membre)
        c = self.registre.find_certificat_by_name(certificat)
        if not (m and c):
            return
        else:
            if not confirm(ls.strings.CLEAR_HISTORY(m.id, c.nom)):
                return
            self.rendre_certificateur.hide()
            self.registre.decerner_certificat(m, c, self.registre.NonCertifie)
            self.reinitialiser.hide()
            self.registre_updated_flag = True
            self.update()

    def imprimer_callback(self):
        """ generates a printable excel file """
        excel.generer_registre(self.registre)

    def upload_in_thread(self):
        """ uploads local register to cloud in separate thread """
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

        self.registre.enregistrer()
        self.thread.start()

    def download_in_thread(self):
        """ downloads register from cloud to local
            file in separate thread """
        if self.thread_running_flag:
            return
        else:
            self.thread_running_flag = True
        self.thread = QThread()
        self.downloader = multithreading.Downloader()
        self.downloader.moveToThread(self.thread)
        self.thread.started.connect(self.downloader.run)
        self.downloader.finished.connect(self.thread.quit)
        self.downloader.finished.connect(self.downloader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def finished():
            self.registre.charger()
            self.update_comboboxes()
            self.update()
            self.thread_progress.setText(ls.strings.SAVED)
            self.thread_running_flag = False

        def started():
            self.thread_progress.setText(ls.strings.SYNCHRONIZING)

        self.downloader.finished.connect(finished)
        self.downloader.started.connect(started)

        self.thread.start()

    def check_connection_in_thread(self):
        """ continously checks if app is connected to internet """
        self.check_thr = QThread()
        self.checker = multithreading.ConnectionChecker()
        self.checker.moveToThread(self.check_thr)
        self.check_thr.started.connect(self.checker.run)
        self.checker.finished.connect(self.check_thr.quit)
        self.checker.finished.connect(self.checker.deleteLater)
        self.check_thr.finished.connect(self.check_thr.deleteLater)
        self.check_thr.start()


if __name__ == "__main__":
    ls.init()
    app = QApplication(sys.argv)
    window = MainUsage()
    window.show()
    app.exec_()

