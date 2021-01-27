# coding: utf-8

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import cloud_support

class Uploader(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    def run(self):
        self.started.emit()
        cloud_support.upload_registre()
        self.finished.emit()

