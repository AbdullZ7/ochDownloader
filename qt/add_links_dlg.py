import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.misc import links_parser

from PySide.QtGui import *
from PySide.QtCore import *


class AddLinks(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(_('Select Folder'))
        self.resize(500, 330)
        
        self.links_list = []
        
        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)
        
        group_log = QGroupBox(_('Paste Your Links (one link per line):'))
        vbox_log = QVBoxLayout()
        group_log.setLayout(vbox_log)
        vbox.addWidget(group_log)
        
        self.text_view = QPlainTextEdit()
        #self.text_view.setReadOnly(True)
        
        vbox_log.addWidget(self.text_view)
        
        hbox = QHBoxLayout()
        hbox.addStretch(0)
        vbox.addLayout(hbox)
        
        btn_close = QPushButton(_('Close'))
        btn_close.clicked.connect(self.reject)
        btn_close.setFixedHeight(35)
        btn_close.setMaximumWidth(80)
        hbox.addWidget(btn_close)
        
        btn_ok = QPushButton(_('OK'))
        btn_ok.clicked.connect(self.on_ok)
        btn_ok.setDefault(True)
        btn_ok.setFixedHeight(35)
        btn_ok.setMaximumWidth(80)
        hbox.addWidget(btn_ok)
        
        self.exec_()
    
    def on_ok(self):
        self.links_list = links_parser(self.text_view.toPlainText())
        self.accept()

    #def reject(self): #on X close button
        #reimplemented.
        #self.hide()
        #return QDialog.Rejected
