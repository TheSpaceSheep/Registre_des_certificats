# coding: utf-8
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt

def init():
    global strings
    strings = None

def select_language(language):
    global strings
    user_lang = "en"
    if language == "fr":
        import lang.fr
        loc_strings = lang.fr.StringsFR()
    elif language == "en":
        import lang.en
        loc_strings = lang.en.StringsEN()
    else:
        import lang.en
        loc_strings = lang.en.StringsEN()

    def valider_callback():
        global strings
        if languages.currentText() == "English":
            user_lang = "en"
        elif languages.currentText() == "Français":
            user_lang = "fr"
        else:
            user_lang = "en"

        if user_lang == "fr":
            import lang.fr
            strings = lang.fr.StringsFR()
        elif user_lang == "en":
            import lang.en
            strings = lang.en.StringsEN()
        else:
            import lang.en
            strings = lang.en.StringsEN()

        with open("lang.rc", "w") as f:
            f.write(user_lang)

        d.close()

    d = QDialog()
    w = QWidget(d)
    l = QVBoxLayout()
    label = QLabel(loc_strings.SELECT_LANGUAGE)
    languages = QComboBox()
    languages.insertItems(0, ["English", "Français"])
    ok = QPushButton(loc_strings.VALIDATE)
    ok.clicked.connect(valider_callback)
    d.setWindowTitle(loc_strings.SELECT_LANGUAGE)
    d.setWindowModality(Qt.ApplicationModal)

    l.addWidget(label)
    l.addWidget(languages)
    l.addWidget(ok)
    w.setLayout(l)
    d.resize(w.sizeHint())
    d.exec_()


def load_language():
    global strings
    try:
        with open("lang.rc", "r") as f:
            user_lang = f.read()

        if user_lang == "fr":
            import lang.fr
            strings = lang.fr.StringsFR()
        elif user_lang == "en":
            import lang.en
            strings = lang.en.StringsEN()
        else:
            import lang.en
            strings = lang.en.StringsEN()

        return True

    except FileNotFoundError:
        return False


