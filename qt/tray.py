import os
import weakref
import logging
logger = logging.getLogger(__name__)

#GUI
from PySide.QtGui import *
from PySide.QtCore import *

import core.cons as cons
from core import events
from core.conf_parser import conf

import signals

ICON_INFO = QSystemTrayIcon.Information
ICON_WARN = QSystemTrayIcon.Warning
ICON_CRITICAL = QSystemTrayIcon.Critical


class Tray(QSystemTrayIcon):
    def __init__(self, parent):
        QSystemTrayIcon.__init__(self, parent)
        self.weak_parent = weakref.ref(parent)
        if self.is_available():
            self.setIcon(QIcon(os.path.join(cons.MEDIA_PATH, "misc", "ochd.ico")))
            self.setToolTip(cons.APP_TITLE)
            self.activated.connect(self.restore)
            self.messageClicked.connect(self.show_window)
            self.context_menu()
            #QApplication.setQuitOnLastWindowClosed(False)

    @property
    def parent(self):
        return self.weak_parent()

    def is_available(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            return True
        return False

    def restore(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_or_hide()

    def show_or_hide(self):
        if self.parent.isVisible():
            self.parent.hide()
        else:
            self.show_window()

    def show_window(self):
        if self.parent.isMaximized():
            self.parent.showMaximized()
        else:
            self.parent.showNormal()
        self.parent.activateWindow()

    def context_menu(self):
        self.menu = QMenu()

        items = [(_('Show/Hide'), self.show_or_hide),
                (None, None),
                (_('Quit'), self.parent.event_close)]

        [self.menu.addAction(title, callback) if title is not None else self.menu.addSeparator()
         for title, callback in items]

        self.setContextMenu(self.menu)

    def show_message(self, title, msg, icon=ICON_INFO, duration=15):
        self.showMessage(title, msg, icon, duration * 1000)

    def connect_messages(self):
        events.captcha_dialog.connect(self.show_catpcha_message)
        events.all_downloads_complete.connect(self.show_all_downloads_complete_message)
        signals.captured_links_count.connect(self.show_captured_links_message)

    def disconnect_messages(self):
        events.captcha_dialog.disconnect(self.show_catpcha_message)
        events.all_downloads_complete.disconnect(self.show_all_downloads_complete_message)
        signals.captured_links_count.disconnect(self.show_captured_links_message)

    def show_captured_links_message(self, count):
        self.show_message('{} {}'.format(count, _('link(s) were captured')), None)

    def show_catpcha_message(self, *args, **kwargs):
        self.show_message(_('Captcha required'), _('You should fill the captcha.'))

    def show_all_downloads_complete_message(self, *args, **kwargs):
        self.show_message(_('All downloads are complete'), None)