# coding: utf-8
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Contains :
# - PyQt widget subclasses to adjust widget behavior
# - Utility functions for dialogs

class MyComboBox(QComboBox):
    def __init__(self, placeholder="Enter Text"):
        super(MyComboBox, self).__init__()
        self.setEditable(True)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.lineEdit().setPlaceholderText(placeholder)
        self.setCurrentIndex(-1)

    def addItems(self, texts):
        super(MyComboBox, self).addItems(texts)
        self.setCurrentIndex(-1)


class MyLineEdit(QLineEdit):
    def __init__(self, placeholder="Enter Text"):
        super(MyLineEdit, self).__init__(placeholderText=placeholder)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(sizePolicy)


def resizeText(widget, e, fixed=None):
    default_size = 9
    size = widget.height()//3 if fixed is None else fixed

    if size > default_size:
        f = QFont('unknown', size)
    else:
        f = QFont('unknown', default_size)
    widget.setFont(f)


class ResizableButton(QPushButton):
    def __init__(self, text=""):
        super(ResizableButton, self).__init__(text)

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.resizeEvent = lambda x: resizeText(self, x)


class ResizableLabel(QLabel):
    def __init__(self, text=""):
        super(ResizableLabel, self).__init__(text)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

class ResizableListWidget(QListWidget):
    def __init__(self):
        super(ResizableListWidget, self).__init__()

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

    def sizeHint(self):
        size = QSize(15*9, 0)
        return size

    def minimumSizeHint(self):
        size = QSize(15*9, 20)
        return size


def confirm(message="Confirmer ?"):
    """displays a message with an "ok" and "cancel" button"""
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Information)

    dialog.setText(message)
    dialog.setWindowTitle("Confirmation")
    dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    retval = dialog.exec_()
    return retval == QMessageBox.Ok

def dialog(msg, title="Information"):
    """displays a simple dialog window with a message"""
    dialog = QMessageBox()
    dialog.setText(msg)
    dialog.setWindowTitle(title)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()

