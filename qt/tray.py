import os
import logging
logger = logging.getLogger(__name__)

#GUI
from PySide.QtGui import *
from PySide.QtCore import *

import media
import core.cons as cons


class Tray:
    def __init__(self, parent):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.available = True
            self.tray_icon = QSystemTrayIcon(parent)
            self.tray_icon.setIcon(QIcon(os.path.join(cons.MEDIA_PATH, "misc", "ochd.ico")))
            self.context_menu(parent)
            #QApplication.setQuitOnLastWindowClosed(False)
            self.tray_icon.show()
        else:
            self.available = False

    def context_menu(self, parent):
        self.menu = QMenu()

        items = [('Minimize', parent.hide),
                ('Maximize', parent.showMaximized),
                ('Restore', parent.showNormal),
                (None, None),
                ('Quit', parent.close)]

        [self.menu.addAction(title, callback) if title is not None else self.menu.addSeparator()
         for title, callback in items]

        self.tray_icon.setContextMenu(self.menu)