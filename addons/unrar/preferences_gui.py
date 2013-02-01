import os
import logging
logger = logging.getLogger(__name__)

from core.conf_parser import conf
from core import cons

from passwords_handler import passwords_handler

from PySide.QtGui import *
from PySide.QtCore import *

PWD_FILE_PATH = os.path.join(cons.APP_PATH, "pwd.txt")
#Config parser
OPTION_UNRAR_REMOVE_FILES = "unrar_remove_files"


class Preferences(QVBoxLayout):
    """"""
    def __init__(self):
        """"""
        QVBoxLayout.__init__(self)

        # Options
        frame = QGroupBox(_('Options:'))

        label_remove_files = QLabel(_('Delete files after extract:'))
        self.remove_files_box = QCheckBox()

        vbox = QVBoxLayout()
        frame.setLayout(vbox)

        hbox_remove_files = QHBoxLayout()
        hbox_remove_files.addWidget(label_remove_files)
        hbox_remove_files.addWidget(self.remove_files_box)
        hbox_remove_files.addStretch()
        vbox.addLayout(hbox_remove_files)

        self.addWidget(frame)

        # Passwords
        frame2 = QGroupBox(_("Passwords (one per line):"))

        vbox2 = QVBoxLayout()
        frame2.setLayout(vbox2)
        
        self.text_view = QPlainTextEdit()
        vbox2.addWidget(self.text_view)
        
        self.addWidget(frame2)
        
        self.load_pwd()
    
    def load_pwd(self):
        """"""
        pwd_set = passwords_handler.get_passwords()
        lines = "\n".join(pwd_set)
        
        if lines:
            self.text_view.setPlainText(lines)
    
    def load(self):
        """"""
        if conf.get_addon_option(OPTION_UNRAR_REMOVE_FILES, default=False, is_bool=True):
            self.remove_files_box.toggle() #activate
        self.load_pwd()
    
    def save(self):
        """"""
        conf.set_addon_option(OPTION_UNRAR_REMOVE_FILES, self.remove_files_box.isChecked(), is_bool=True)
        #
        txt = self.text_view.toPlainText()
        passwords_handler.replace(txt.splitlines())
        passwords_handler.save()