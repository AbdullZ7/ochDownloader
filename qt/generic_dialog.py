from PySide.QtGui import *
from PySide.QtCore import *


class Dialog(QDialog):
    """"""
    def __init__(self, parent, title, widget):
        """"""
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(title)
        self.resize(340, 200)

        self.parent = parent

        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)

        vbox.addWidget(widget)

        #buttons
        vbox.addStretch()

        hbox_btns = QHBoxLayout()
        vbox.addLayout(hbox_btns)

        hbox_btns.addStretch()

        btn_cancel = QPushButton(_('Cancel'))
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setFixedHeight(35)
        btn_cancel.setMaximumWidth(80)
        hbox_btns.addWidget(btn_cancel)

        btn_ok = QPushButton(_('OK'))
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setFixedHeight(35)
        btn_ok.setMaximumWidth(80)
        hbox_btns.addWidget(btn_ok)

        #if hasattr(widget, 'setFocus'):
            #widget.setFocus() #call after creating all of the other widgets.

        self.exec_()