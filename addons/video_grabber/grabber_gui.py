import logging
logger = logging.getLogger(__name__)

from PySide.QtGui import *
from PySide.QtCore import *


class GrabberDialog(QDialog):
    """"""
    def __init__(self, parent):
        """"""
        #TODO: change textEdit to "searching" text on OK, add links after finish.
        #or else show an error message.
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(_('Video Grabber'))
        self.resize(340, 200)

        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)

        group_log = QGroupBox(_('Paste Your Links (one link per line):'))
        vbox_log = QVBoxLayout()
        group_log.setLayout(vbox_log)
        vbox.addWidget(group_log)

        self.text_view = QPlainTextEdit()

        vbox_log.addWidget(self.text_view)

        hbox = QHBoxLayout()
        hbox.addStretch(0)
        vbox.addLayout(hbox)

        btn_close = QPushButton(_('Cancel'))
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
        #self.links_list = links_parser(self.text_view.toPlainText())
        self.accept()