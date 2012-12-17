import logging
logger = logging.getLogger(__name__)

from core import cons

from PySide.QtGui import *
from PySide.QtCore import *

if cons.OS_WIN:
    from qt.misc import flash_wnd
else:
    flash_wnd = None


class QualityChoiceDialog(QDialog):
    """"""
    def __init__(self, f_name, choices_dict, parent):
        """"""
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle("{f_name}".format(f_name=f_name))
        self.resize(340, 200)

        self.choices_dict = choices_dict
        self.solution = None

        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)

        #captcha image
        self.cb = QComboBox()
        [self.cb.addItem(quality) for quality in self.choices_dict.values()]
        vbox.addWidget(self.cb)

        #buttons
        vbox.addStretch()

        hbox_btns = QHBoxLayout()
        vbox.addLayout(hbox_btns)

        hbox_btns.addStretch()

        btn_ok = QPushButton(_('OK'))
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.on_ok)
        btn_ok.setFixedHeight(35)
        btn_ok.setMaximumWidth(80)
        hbox_btns.addWidget(btn_ok)

        self.cb.setFocus() #call after creating all of the other widgets.

        #Flash if the window is in the background.
        if flash_wnd is not None:
            flash_wnd.flash_taskbar_icon(parent.winId())

        self.exec_()

    def get_solution(self):
        return self.solution

    def on_ok(self):
        quality = self.cb.currentText()
        if quality:
            choice_dict = {quality: id_ for id_, quality in self.choices_dict.iteritems()}
            self.solution = choice_dict.get(quality, None)
        self.accept()

    def reject(self, *args, **kwargs):
        self.on_ok()
        QDialog.reject(self, *args, **kwargs)