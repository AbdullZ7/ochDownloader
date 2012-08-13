import logging
logger = logging.getLogger(__name__)

from core.conf_parser import conf
import core.cons as cons

from PySide.QtGui import *
from PySide.QtCore import *

import clipboard_gui


class Preferences(QVBoxLayout):
    """"""
    def __init__(self):
        """"""
        #TODO: add activator
        QVBoxLayout.__init__(self)

        frame = QGroupBox(_('Extensions to catch:'))

        vbox = QVBoxLayout()
        frame.setLayout(vbox)

        hbox_exts = QHBoxLayout()

        label_extensions = QLabel(_('Activate:'))
        self.exts_box = QCheckBox()
        self.exts_box.toggled.connect(self.on_toggled)

        hbox_exts.addWidget(label_extensions)
        hbox_exts.addWidget(self.exts_box)
        hbox_exts.addStretch()
        vbox.addLayout(hbox_exts)

        self.exts_line = QLineEdit()
        vbox.addWidget(self.exts_line)

        self.addWidget(frame)

        self.addStretch()

        self.on_toggled()

    def on_toggled(self):
        if self.exts_box.isChecked():
            self.exts_line.setEnabled(True)
        else:
            self.exts_line.setEnabled(False)

    def load(self):
        """"""
        if conf.get_addon_option(clipboard_gui.OPTION_CLIPBOARD_ACTIVE, default=True, is_bool=True):
            self.exts_box.toggle() #activate
        exts = conf.get_addon_option(clipboard_gui.OPTION_CLIPBOARD_EXTS) or clipboard_gui.EXTS
        self.exts_line.setText(exts)

    def save(self):
        """"""
        exts_activate = "True" if self.exts_box.isChecked() else "False"
        conf.set_addon_option(clipboard_gui.OPTION_CLIPBOARD_ACTIVE, exts_activate)
        conf.set_addon_option(clipboard_gui.OPTION_CLIPBOARD_EXTS, self.exts_line.text())
