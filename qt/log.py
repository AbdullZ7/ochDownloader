import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.misc import tail, smart_decode #read file from bottom.

from PySide.QtGui import *
from PySide.QtCore import *


class Log(QVBoxLayout):
    def __init__(self, parent=None):
        QVBoxLayout.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)
        
        self.text_view = QPlainTextEdit()
        self.text_view.setReadOnly(True)
        
        self.addWidget(self.text_view)
    
        btn_view_log = QPushButton(_('View Full Log'))
        btn_view_log.clicked.connect(self.on_view_log)
        btn_view_log.setFixedHeight(35)
        btn_view_log.setMaximumWidth(180)
        self.addWidget(btn_view_log)
    
    def on_load(self):
        """
        load the last few lines of the file.log
        This method is suppose to be called on switch-tab event (main_gui)
        """
        try:
            with open(cons.LOG_FILE, "rb") as fh:
                last_lines = tail(fh) #misc function
        except EnvironmentError as err:
            last_lines = str(err)
            logger.warning("{0}".format(err))
        
        self.text_view.setPlainText(smart_decode(last_lines))

    def on_view_log(self):
        view_full_log = ViewFullLog()


class ViewFullLog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(_('Full Log File'))
        self.resize(500, 330)
        
        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)
        
        group_log = QGroupBox(_('Activity Log:'))
        vbox_log = QVBoxLayout()
        group_log.setLayout(vbox_log)
        vbox.addWidget(group_log)
        
        self.text_view = QPlainTextEdit()
        self.text_view.setReadOnly(True)
        
        vbox_log.addWidget(self.text_view)
        
        hbox = QHBoxLayout()
        hbox.addStretch(0)
        vbox.addLayout(hbox)
        
        btn_close = QPushButton(_('Close'))
        btn_close.clicked.connect(self.close)
        btn_close.setFixedHeight(35)
        btn_close.setMaximumWidth(80)
        hbox.addWidget(btn_close)
        
        self.load_full_log()
        
        self.exec_()
        
    def load_full_log(self):
        """"""
        try:
            with open(cons.LOG_FILE, "rb") as fh:
                lines = fh.read()
        except EnvironmentError as err:
            lines = str(err)
            #logger.warning("{0}".format(err))
        
        self.text_view.setPlainText(smart_decode(lines))
