# coding: utf-8

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import time

import cloud_support
import widgets
import language_selector as ls

class Uploader(QObject):
    """calls upload function from a thread"""
    started = pyqtSignal()
    finished = pyqtSignal()
    def run(self):
        self.started.emit()
        cloud_support.upload_registre()
        self.finished.emit()

class Downloader(QObject):
    """calls download function from a thread"""
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
    """Checks connection every 3 seconds and
    displays a dialog if there is no connection
    Application must always be connected to be usable"""
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
            except socket.gaierror:
                widgets.dialog(ls.strings.CHECK_INTERNET_CONNECTION, ls.strings.ERROR)
            time.sleep(3)


