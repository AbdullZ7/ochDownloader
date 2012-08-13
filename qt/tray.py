import os
import logging
logger = logging.getLogger(__name__)

#GUI
from PySide.QtGui import *
from PySide.QtCore import *

import core.cons as cons
from core.conf_parser import conf


class Tray:
    def __init__(self, parent):
        self.parent = parent
        self.available = False
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(parent)
            self.tray_icon.setIcon(QIcon(os.path.join(cons.MEDIA_PATH, "misc", "ochd.ico")))
            self.tray_icon.setToolTip(cons.APP_TITLE)
            self.tray_icon.activated.connect(self.restore)
            self.context_menu()
            #QApplication.setQuitOnLastWindowClosed(False)
            if conf.get_tray_available():
                self.available = True
                self.tray_icon.show()

    def restore(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.parent.showNormal()

    def show_or_hide(self):
        if self.parent.isVisible():
            self.parent.hide()
        else:
            self.parent.showNormal()

    def context_menu(self):
        self.menu = QMenu()

        items = [(_('Show/Hide'), self.show_or_hide),
                (None, None),
                (_('Quit'), self.parent.event_close)]

        [self.menu.addAction(title, callback) if title is not None else self.menu.addSeparator()
         for title, callback in items]

        self.tray_icon.setContextMenu(self.menu)