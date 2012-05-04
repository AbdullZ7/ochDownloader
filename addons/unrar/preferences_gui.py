import sys
import os
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.config import config_parser
import core.cons as cons

from passwords_handler import passwords_handler

from PySide.QtGui import *
from PySide.QtCore import *

PWD_FILE_PATH = os.path.join(cons.APP_PATH, "pwd.txt")


class Preferences(QVBoxLayout):
    """"""
    def __init__(self):
        """"""
        QVBoxLayout.__init__(self)
        
        frame = QGroupBox(_("Passwords (one per line):"))
        
        self.text_view = QPlainTextEdit()
        vbox = QVBoxLayout()
        frame.setLayout(vbox)
        vbox.addWidget(self.text_view)
        
        self.addWidget(frame)
        
        self.load_pwd()
    
    def load_pwd(self):
        """"""
        pwd_set = passwords_handler.get_passwords()
        lines = "\n".join(pwd_set)
        
        if lines:
            self.text_view.setPlainText(lines)
    
    def load(self):
        """"""
        self.load_pwd()
    
    def save(self):
        """"""
        txt = self.text_view.toPlainText()
        passwords_handler.replace(txt.splitlines())
        passwords_handler.save()
