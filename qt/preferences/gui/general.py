from core.config import conf

from PySide.QtGui import *
from PySide.QtCore import *

from qt import signals


class General(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, _('General:'))

        #vbox_general = QVBoxLayout()
        grid_general = QGridLayout()
        self.setLayout(grid_general)

        label_tray = QLabel(_('System tray icon:'))
        self.tray_box = QCheckBox()
        grid_general.addWidget(label_tray, 1, 0)
        grid_general.addWidget(self.tray_box, 1, 1)

        label_tab = QLabel(_('Auto tab switching:'))
        self.switch_tab_box = QCheckBox()
        grid_general.addWidget(label_tab, 2, 0)
        grid_general.addWidget(self.switch_tab_box, 2, 1)

        #
        grid_general.setColumnStretch(2, 1)

    def load(self):
        if conf.get_tray_available():
            self.tray_box.toggle()
        if conf.get_auto_switch_tab():
            self.switch_tab_box.toggle()

    def save(self):
        tray = self.tray_box.isChecked()
        old_tray_value = conf.get_tray_available()
        conf.set_tray_available(tray)
        if tray != old_tray_value:
            signals.show_or_hide_tray.emit()
        switch_tab = self.switch_tab_box.isChecked()
        conf.set_auto_switch_tab(switch_tab)
