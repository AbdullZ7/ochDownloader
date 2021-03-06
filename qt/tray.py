import os
import weakref
import logging
logger = logging.getLogger(__name__)

#GUI
from PySide.QtGui import *
from PySide.QtCore import *

from core import cons
from core import events

import signals
from context_menu import Menu

ICON_INFO = QSystemTrayIcon.Information
ICON_WARN = QSystemTrayIcon.Warning
ICON_CRITICAL = QSystemTrayIcon.Critical


class Tray(QSystemTrayIcon):
    def __init__(self, parent):
        QSystemTrayIcon.__init__(self)
        self.weak_parent = weakref.ref(parent)
        self.setIcon(QIcon(os.path.join(cons.MEDIA_PATH, "misc", "ochd.ico")))
        self.setToolTip(cons.APP_TITLE)
        self.activated.connect(self.restore)
        self.messageClicked.connect(self.show_window)
        self.context_menu()

    @property
    def parent(self):
        return self.weak_parent()

    def is_available(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            return True
        return False

    def show(self):
        #overriden
        QSystemTrayIcon.show(self)
        self.connect_messages()

    def hide(self):
        #overriden
        QSystemTrayIcon.hide(self)
        self.disconnect_messages()

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
        options = [(_('Show/Hide'), self.show_or_hide, True),
                   None,
                   (_('Quit'), self.parent.event_close, True)]
        self.menu = Menu(options)
        self.setContextMenu(self.menu)

    def show_message(self, title, msg, icon=ICON_INFO, duration=15):
        self.showMessage(title, msg, icon, duration * 1000)

    def connect_messages(self):
        # TODO: add signal to show messages
        #signals.captcha_dialog.connect(self.show_catpcha_message)
        events.all_downloads_complete.connect(self.show_all_downloads_complete_message)
        signals.captured_links_count.connect(self.show_captured_links_message)

    def disconnect_messages(self):
        #signals.captcha_dialog.disconnect(self.show_catpcha_message)
        events.all_downloads_complete.disconnect(self.show_all_downloads_complete_message)
        signals.captured_links_count.disconnect(self.show_captured_links_message)

    def show_captured_links_message(self, count):
        self.show_message('{} {}'.format(count, _('link(s) were captured')), None)

    def show_catpcha_message(self, *args, **kwargs):
        self.show_message(_('Captcha required'), _('You should fill the captcha.'))

    def show_all_downloads_complete_message(self, *args, **kwargs):
        self.show_message(_('All downloads are complete'), None)