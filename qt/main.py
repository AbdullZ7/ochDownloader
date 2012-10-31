import traceback
import gettext
import locale
import os
import logging
logger = logging.getLogger(__name__)
#Libs
#from core.Container_Extractor import Container
from core.conf_parser import conf
from core import events
from core.api import api
from core import cons

#GUI
from PySide.QtGui import *
from PySide.QtCore import *

import media
import signals
from status_bar import StatusBar
from downloads import Downloads
from add_downloads import AddDownloads
from log import Log
from accounts import ConfigAccounts
from about import About
from preferences.preferences import Preferences
from addons import AddonsManager
from tray import Tray
from idle_queue_dispatcher import ThreadDispatcher


MIN_WIDTH = 550
MIN_HEIGHT = 250
BTN, ICON, TITLE, CALLBACK, SENSITIVE = range(5)

def init_gettext():
    """Internationalization"""
    #locale_langs = [lang for lang in os.listdir(cons.LOCALE_PATH) if os.path.isdir(os.path.join(cons.LOCALE_PATH, lang))]
    #supported_langs = [lang.split("/")[-3] for lang in gettext.find(cons.APP_NAME, cons.LOCALE_PATH, all=True)] #locale_langs, all=True)]
    lc, encoding = locale.getdefaultlocale()
    default_lang = lc.split("_")[0]
    #default_lang = "ro"
    #default_lang = lc.replace("_", "-").lower()
    #if default_lang not in supported_langs:
        #for lang in supported_langs:
            #if lang.split("-")[0] == default_lang.split("-")[0]:
                #default_lang = lang
                #break
    lang = gettext.translation(cons.APP_NAME, cons.LOCALE_PATH, languages=[default_lang, ], fallback=True)
    lang.install(cons.APP_NAME, cons.LOCALE_PATH) #install _() on builtins namespace

#Catch Unhandled Exceptions...
def excepthook(exc_type, exc_value, tb):
    """"""
    message = "Unhandled exception: "
    message += "".join(traceback.format_exception(exc_type, exc_value, tb))
    logger.critical(message)
    halt()

#and close GUI.
def halt():
    """
    TODO: Mostrar ventana de error y cerrar apropiadamente.
    """
    for window in QApplication.topLevelWidgets():
        if isinstance(window, Gui):
            window.can_close = True
            window.close()
        #window.hide()


class Gui(QMainWindow):
    def __init__(self):
        #TODO: REFACTORY
        QMainWindow.__init__(self)
        
        self.setWindowTitle(cons.APP_TITLE)
        self.setWindowIcon(QIcon(os.path.join(cons.MEDIA_PATH, "misc", "ochd.ico")))
        self.resize(MIN_WIDTH, MIN_HEIGHT)
        self.center()
        
        self.restore_wnd_geometry()

        self.downloads = Downloads(self)
        self.add_downloads = AddDownloads(self)
        self.log = Log(self)
        
        self.stop = (QToolButton(), media.get_icon(media.STOP, media.MEDIUM), _('Stop Download'), self.on_stop_download, False)
        self.start = (QToolButton(), media.get_icon(media.START, media.MEDIUM), _('Start Download'), self.on_start_download, False)
        accounts = (QToolButton(), media.get_icon(media.ACCOUNTS, media.MEDIUM), _('Accounts'), self.on_accounts, True)
        preferences = (QToolButton(), media.get_icon(media.PREFERENCES, media.MEDIUM), _('Preferences'), self.on_preferences, True)
        about = (QToolButton(), media.get_icon(media.ABOUT, media.MEDIUM), _('About'), self.on_about, True)
        
        self.menu = QMenu()
        preferences[BTN].setPopupMode(QToolButton.MenuButtonPopup)
        preferences[BTN].setMenu(self.menu)
        
        toolbar = Toolbar(self, [self.start, self.stop, None, accounts, preferences, None, about])

        self.toolbar = self.addToolBar(toolbar)

        #self.vbox = QVBoxLayout(self)

        #tabs
        self.previous_tab = None
        self.tab = QTabWidget(self)
        #
        self.tab.addTab(self.downloads, _('Downloads'))
        #
        self.tab_add_downloads = QWidget()
        self.tab_add_downloads.setLayout(self.add_downloads)
        self.tab.addTab(self.tab_add_downloads, _('Add downloads'))
        #
        #addons
        self.addons_manager = AddonsManager(self)
        self.addons_list = self.addons_manager.addons_list
        #...tabs
        self.addon_tab_widgets = []
        self.load_addon_tabs()
        #
        self.tab_log = QWidget()
        self.tab_log.setLayout(self.log)
        self.tab.addTab(self.tab_log, _('Log'))
        #
        self.preferences = Preferences(self.addons_list, self)
        #self.tab.addTab(self.preferences, 'Preferences')
        #
        self.tab.currentChanged.connect(self.on_tab_switch)
        #
        self.setCentralWidget(self.tab)

        #status bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        #drop down menu
        [addon.set_menu_item() for addon in self.addons_list]
        #self.menu.addSeparator()
        #self.menu.addAction('Preferences', self.on_preferences)

        #system tray icon
        self.tray = Tray(self)
        if self.tray.available:
            self.can_close = False
        else:
            self.can_close = True

        #load session.
        self.load_session()

        #add core's event loop
        #self.idle_timeout(500, self.queue_loop)
        self.dispatcher = ThreadDispatcher(self)
        self.dispatcher.start()

        #quit event
        events.quit.connect(self.event_close)

        #custom qt signals
        signals.switch_tab.connect(self.switch_tab)

        self.show()

    def customEvent(self, event):
        #process idle_queue_dispacher events
        event.callback()

    def switch_tab(self, index):
        self.tab.setCurrentIndex(index)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def restore_wnd_geometry(self):
        wx, wy, ww, wh = QDesktopWidget().availableGeometry().getRect()
        x, y, w, h = conf.get_window_settings()
        if ww <= w or wh <= h:
            self.showMaximized()
        elif ww > x >= 0 and wh > y >= 0: #resize and move
            self.setGeometry(x, y, w, h)
        else: #resize only
            self.resize(w, h)
    
    def on_stop_download(self):
        rows = self.downloads.get_selected_rows()
        if rows:
            for row in rows:
                items = self.downloads.items
                id_item = items[row][0]
                stopped = api.stop_download(id_item) #return true or false
                if stopped:
                    if items[row][1] == self.downloads.icons_dict[cons.STATUS_QUEUE]:
                        items[row][1] = self.downloads.icons_dict[cons.STATUS_STOPPED]
                    self.stop[BTN].setEnabled(False) #deshabilitar el boton de stop ya que acaban de detener la descarga.
                    self.start[BTN].setEnabled(True)
    
    def on_start_download(self):
        rows = self.downloads.get_selected_rows()
        if rows:
            #id_item = model[row][0]
            for row in rows:
                items = self.downloads.items
                id_item = items[row][0]

                #TODO: Implementar lo mismo pero para stopped (buscar en lista stopped y finished para comparar)
                started = api.start_download(id_item) #return true or false
                if started:
                    items[row][1] = self.downloads.icons_dict[cons.STATUS_QUEUE] #status
                    items[row][10] = None #status_msg
                    self.stop[BTN].setEnabled(True) #deshabilitar el boton de stop ya que acaban de detener la descarga.
                    self.start[BTN].setEnabled(False)
                
            #self.downloads.get_status() #iniciar update de lista.
            id_item_list = [row[0] for row in items]
            api.reorder_queue(id_item_list)
    
    def on_accounts(self):
        accounts = ConfigAccounts(self)
    
    def on_preferences(self):
        index_page = self.tab.indexOf(self.preferences) #get the page containig the widget
        if index_page >= 0: #if = -1 there is not such tab.
            self.tab.setCurrentIndex(index_page)
        else:
            index_page = self.tab.addTab(self.preferences, _('Preferences'))
            btn_close = QPushButton(self)
            #btn_close.setIcon(QIcon('stop.png'))
            #btn_close.setIconSize(QSize(10, 10))
            btn_close.setFixedHeight(12)
            btn_close.setFixedWidth(12)
            #btn_close.setFlat(True)
            btn_close.clicked.connect(self.on_close_preferences)
            self.tab.tabBar().setTabButton(index_page, QTabBar.RightSide, btn_close)
            #
            last_index = self.tab.count() - 1
            self.tab.setCurrentIndex(last_index)
    
    def on_close_preferences(self):
        index_page = self.tab.indexOf(self.preferences)
        if index_page >= 0:
            self.tab.removeTab(index_page)
        #self.tab.setCurrentIndex(0)
    
    def on_about(self):
        about = About(self)
    
    def on_tab_switch(self, index):
        current_widget = self.tab.currentWidget()
        if current_widget == self.tab_log:
            self.log.on_load()
        elif current_widget in self.addon_tab_widgets:
            tab = current_widget.layout()
            tab.on_load()

        if self.previous_tab == self.preferences:
            self.previous_tab.on_close()
        elif self.previous_tab in self.addon_tab_widgets:
            tab = self.previous_tab.layout()
            tab.on_close()
        self.previous_tab = current_widget
    
    def load_addon_tabs(self):
        for tab, addon in [(addon.get_tab(), addon) for addon in self.addons_list]:
            if tab is not None:
                tab_widget = QWidget()
                tab_widget.setLayout(tab)
                self.tab.addTab(tab_widget, addon.name)
                self.addon_tab_widgets.append(tab_widget)

    def load_session(self):
        """"""
        ordered_list = api.load_session()
        self.downloads.store_items(ordered_list)
    
    def save_session(self):
        """"""
        id_item_list = [row[0] for row in self.downloads.items]
        api.save_session(id_item_list)
    
    def idle_timeout(self, interval, func):
        timer = QTimer(self)
        timer.timeout.connect(func)
        timer.start(interval)
        return timer
    
    #def queue_loop(self):
        #try:
            #callback = idle_loop.get_nowait()
            #callback()
        #except Queue.Empty:
            #pass

    def event_close(self):
        self.can_close = True
        self.close()

    def closeEvent(self, event): #overloaded method
        """
        also useful for any QWidget
        """
        if self.can_close: #if self.canExit():
            x, y, w, h = self.geometry().getRect()
            self.hide()
            self.save_session()
            self.preferences.on_close()
            conf.set_window_settings(x, y, w, h)
            conf.save()
            event.accept()
        else: #hide only
            self.hide()
            event.ignore()


class Toolbar(QToolBar):
    """"""
    def __init__(self, parent, btn_list):
        """
        list = [(tool_name, image, module_handler), ]
        """
        QToolBar.__init__(self, parent)
        for button in btn_list:
            if button is None:
                self.addSeparator()
            else:
                btn, icon, text, callback, is_sensitive = button
                btn.setIcon(icon)
                btn.setText(text)
                btn.setEnabled(is_sensitive)
                btn.clicked.connect(callback)
                self.addWidget(btn)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    gui = Gui()
    app.exec_()
    sys.exit(0)
