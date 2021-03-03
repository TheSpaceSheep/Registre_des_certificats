# coding: utf-8

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import time

import cloud_support
from widgets import*

class Uploader(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    def run(self):
        self.started.emit()
        cloud_support.upload_registre()
        self.finished.emit()

class Downloader(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    def run(self):
        self.started.emit()
        with open("school_name.txt", "r") as f:
            name = f.read()
        with open("p.rc", "r") as f:
            pwd = f.read()

        cloud_support.download_registre(name, pwd)
        self.finished.emit()

class ConnectionChecker(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    def run(self):
        REMOTE_SERVER = "one.one.one.one"
        while 1:
            try:
                # see if we can resolve the host name -- tells us if there is
                # a DNS listening
                host = socket.gethostbyname(REMOTE_SERVER)
                # connect to the host -- tells us if the host is actually
                # reachable
                s = socket.create_connection((host, 80), 2)
                s.close()
                print("Connected.")
            except socket.gaierror:
                dialog("Veuillez vérifier votre connection internet.", "Erreur")
            time.sleep(3)


