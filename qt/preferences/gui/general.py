from core.conf_parser import conf

from PySide.QtGui import *
from PySide.QtCore import *


class General(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, _('General:'))

        #vbox_general = QVBoxLayout()
        grid_general = QGridLayout()
        self.setLayout(grid_general)

        label_tray = QLabel(_('System tray icon (restart required):'))

        self.tray_box = QCheckBox()

        grid_general.addWidget(label_tray, 1, 0)
        grid_general.addWidget(self.tray_box, 1, 1)

        #
        grid_general.setColumnStretch(2, 1)

    def load(self):
        if conf.get_tray_available():
            self.tray_box.toggle()

    def save(self):
        tray = self.tray_box.isChecked()
        conf.set_tray_available(tray)
