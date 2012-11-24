import logging
logger = logging.getLogger(__name__)

from PySide.QtGui import *
from PySide.QtCore import *

from connection.connection_tab import Connection
from gui.gui_tab import GUI
from addons_tab import AddonsTab


class Preferences(QTabWidget):
    def __init__(self, addons_list):
        QTabWidget.__init__(self)
        self.setTabPosition(QTabWidget.West)
        #self.setTabShape(QTabWidget.Triangular)

        self.tab_widgets = []

        self.connection = Connection()
        #self.tab_connection = QWidget()
        #self.tab_connection.setLayout(self.connection)
        self.addTab(self.connection, _('Connection'))
        self.tab_widgets.append(self.connection)
        
        self.addons_tab = AddonsTab(addons_list)
        #self.tab_connection = QWidget()
        #self.tab_connection.setLayout(self.connection)
        self.addTab(self.addons_tab, _('Addons'))
        self.tab_widgets.append(self.addons_tab)

        self.gui = GUI()
        self.addTab(self.gui, _('GUI'))
        self.tab_widgets.append(self.gui)

        self.on_load()

    def on_load(self):
        """"""
        for widget in self.tab_widgets: #polymorphism.
            widget.load()
        logger.debug("Preferences loaded.")

    def on_close(self):
        """"""
        for widget in self.tab_widgets: #polymorphism.
            widget.save()
        logger.debug("Preferences saved.")
