import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import core.cons as cons

from PySide.QtGui import *
from PySide.QtCore import *


class AddonsTab(QTabWidget):
    def __init__(self, addons_list, parent=None):
        QTabWidget.__init__(self)
        
        self.addon_preferences_list = []
        
        for addon in addons_list:
            addon_preferences = addon.get_preferences()
            if addon_preferences is not None:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setEnabled(True)
                tab = QWidget()
                tab.setLayout(addon_preferences)
                scroll.setWidget(tab)
                self.addTab(scroll, addon.name)
                self.addon_preferences_list.append(addon_preferences)
    
    def load(self):
        for addon_pref in self.addon_preferences_list:
            addon_pref.load()
    
    def save(self):
        for addon_pref in self.addon_preferences_list:
            addon_pref.save()
    
