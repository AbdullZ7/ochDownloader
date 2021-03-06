import weakref
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.utils import tail, smart_unicode #read file from bottom.

from PySide.QtGui import *
from PySide.QtCore import *


class Log(QVBoxLayout):
    def __init__(self, parent):
        QVBoxLayout.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)

        self.weak_parent = weakref.ref(parent)
        
        self.text_view = QPlainTextEdit()
        self.text_view.setReadOnly(True)
        
        self.addWidget(self.text_view)
    
        btn_view_log = QPushButton(_('View Full Log'))
        btn_view_log.clicked.connect(self.on_view_log)
        btn_view_log.setFixedHeight(35)
        btn_view_log.setMaximumWidth(180)
        self.addWidget(btn_view_log)

    @property
    def parent(self):
        return self.weak_parent()
    
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
        
        self.text_view.setPlainText(smart_unicode(last_lines))

    def on_view_log(self):
        view_full_log = ViewFullLog(self.parent)


class ViewFullLog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(_('Full Log File'))
        self.resize(340, 200)
        
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
        self.deleteLater()
        
    def load_full_log(self):
        """"""
        try:
            with open(cons.LOG_FILE, "rb") as fh:
                lines = fh.read()
        except EnvironmentError as err:
            lines = str(err)
            #logger.warning("{0}".format(err))
        
        self.text_view.setPlainText(smart_unicode(lines))
