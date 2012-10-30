import os
import logging
logger = logging.getLogger(__name__)

#GUI
from PySide.QtGui import *
from PySide.QtCore import *

import core.cons as cons
from core.events import events
from core.conf_parser import conf

import signals

ICON_INFO = QSystemTrayIcon.Information
ICON_WARN = QSystemTrayIcon.Warning
ICON_CRITICAL = QSystemTrayIcon.Critical


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
                self.connect_messages()

    def restore(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_or_hide()

    def show_or_hide(self):
        if self.parent.isVisible():
            self.parent.hide()
        elif self.parent.isMaximized():
            self.parent.showMaximized()
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

    def show_message(self, title, msg, icon=ICON_INFO, duration=15):
        self.tray_icon.showMessage(title, msg, icon, duration * 1000)

    def connect_messages(self):
        events.captcha_dialog.connect(self.show_catpcha_message)
        events.all_downloads_complete.connect(self.show_all_downloads_complete_message)
        signals.captured_links_count.connect(self.show_captured_links_message)

    def show_captured_links_message(self, count):
        self.show_message('{} {}'.format(count, _('link(s) were captured')), None)

    def show_catpcha_message(self, *args, **kwargs):
        self.show_message(_('Captcha required'), _('You should fill the captcha.'))

    def show_all_downloads_complete_message(self, *args, **kwargs):
        self.show_message(_('All downloads are complete'), None)