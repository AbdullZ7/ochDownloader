import weakref

from PySide.QtGui import *
from PySide.QtCore import *


class UnLockDialog(QDialog):
    """"""
    def __init__(self, parent):
        """"""
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle("Input password")
        self.resize(340, 200)

        self.weak_parent = weakref.ref(parent)

        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)

        #input
        hbox_input = QHBoxLayout()
        vbox.addLayout(hbox_input)

        self.entry_input = QLineEdit()
        hbox_input.addWidget(self.entry_input)

        #buttons
        vbox.addStretch()

        hbox_btns = QHBoxLayout()
        vbox.addLayout(hbox_btns)

        btn_refresh = QPushButton(_('Cancel'))
        btn_refresh.clicked.connect(self.reject)
        btn_refresh.setFixedHeight(35)
        btn_refresh.setMaximumWidth(80)
        hbox_btns.addWidget(btn_refresh)

        btn_ok = QPushButton(_('OK'))
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setFixedHeight(35)
        btn_ok.setMaximumWidth(80)
        hbox_btns.addWidget(btn_ok)

        #note: if does not work, use singleShot timer.
        self.entry_input.setFocus() #call after creating all of the other widgets.

        self.exec_()

    @property
    def parent(self):
        return self.weak_parent()