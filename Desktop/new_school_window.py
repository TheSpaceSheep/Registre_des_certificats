# coding: utf-8
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from widgets import *
import cloud_support

class NewSchoolWindow(QMainWindow):
    def __init__(self, parent):
        super(NewSchoolWindow, self).__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("Charger ou créer un registre")
        main_widget = QWidget()

        self.list_of_schools = cloud_support.fetch_list_of_schools()
        if self.list_of_schools == 1:
            QTimer.singleShot(0, self.close)

        self.layout = QFormLayout()

        self.new_school_l = QLabel("Ecole :")
        self.new_school_c = MyComboBox("Entrer un nom")

        self.pwd_l = QLabel("Mot de passe :")
        self.pwd_c = QLineEdit()

        self.pwd_confirm_l = QLabel("Confirmer mot de passe :")
        self.pwd_confirm_c = QLineEdit()

        self.pwd_check_l = QLabel("Les mots de passe ne correspondent pas")
        self.pwd_check_l.setFont(QFont("arial", 9))
        self.pwd_check_l.setStyleSheet('color: red')

        self.charger_creer = ResizableButton("Valider")
        self.charger_creer.clicked.connect(self.charger_creer_callback)

        self.layout.addRow(self.new_school_l, self.new_school_c)
        self.layout.addRow(self.pwd_l, self.pwd_c)
        self.layout.addRow(self.pwd_confirm_l, self.pwd_confirm_c)
        self.layout.addRow(self.pwd_check_l)
        self.layout.addRow(self.charger_creer)

        self.pwd_c.setEchoMode(QLineEdit.Password)
        self.pwd_confirm_c.setEchoMode(QLineEdit.Password)

        self.pwd_c.textChanged.connect(self.update)
        self.pwd_confirm_c.textChanged.connect(self.update)
        self.new_school_c.addItems(self.list_of_schools)
        self.new_school_c.currentTextChanged.connect(self.update)

        main_widget.setLayout(self.layout)
        self.setCentralWidget(main_widget)

    def closeEvent(self, event):
        super(NewSchoolWindow, self).closeEvent(event)
        self.parentWidget().hide_widgets()
        self.parentWidget().close_avance()


    def showEvent(self, event):
        super(NewSchoolWindow, self).showEvent(event)
        self.pwd_check_l.hide()
        self.charger_creer.hide()
        self.pwd_confirm_c.hide()
        self.pwd_confirm_l.hide()


    def update(self):
        self.check_passwords()
        t = self.new_school_c.currentText()
        if t == "":
            self.charger_creer.hide()
            self.pwd_confirm_c.hide()
            self.pwd_confirm_l.hide()
            self.pwd_confirm_c.setText("")
        elif t not in self.list_of_schools:
            self.charger_creer.setText("Créer registre")
            self.charger_creer.show()
            if self.pwd_c.text() != "":
                self.pwd_confirm_c.show()
                self.pwd_confirm_l.show()
        else:
            self.charger_creer.setText("Charger registre")
            self.charger_creer.show()
            self.pwd_confirm_c.hide()
            self.pwd_confirm_l.hide()

    def check_passwords(self):
        p1 = self.pwd_c.text()
        p2 = self.pwd_confirm_c.text()
        if p1 != p2 and p1 != "" and p2 != "":
            self.pwd_check_l.show()
            return False
        else:
            self.pwd_check_l.hide()
            return True

    def charger_creer_callback(self):
        ecole = self.new_school_c.currentText()
        pwd = self.pwd_c.text()
        creer = self.new_school_c.currentText() not in self.list_of_schools

        if creer and confirm(f"Créer un registre des certificats pour l'école {ecole} ?"):
            if cloud_support.creer_ecole(ecole, pwd):
                self.list_of_schools.append(ecole)
                dialog(f"Le registre pour l'école {ecole} a bien été créé.")
                self.parentWidget().parentWidget().school_name = ecole
                self.close()
                self.parentWidget().update()

        else:
            try:
                if cloud_support.charger_ecole(ecole, pwd):
                    dialog(f"Le registre pour l'école {ecole} a bien été chargé.")
                    self.parentWidget().parentWidget().school_name = ecole
                    self.close()
                    self.parentWidget().close()
            except ValueError:
                print("mot de passe erroné")
