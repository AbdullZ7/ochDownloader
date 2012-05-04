import gtk
import pygtk

import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import core.cons as cons
from core.config import config_parser

from gui.notebook_gui import Notebook

from addons_tab import AddonsTab
from connection.connection_tab import ConnectionTab


class Preferences(gtk.VBox):
    """"""
    def __init__(self, addons_list):
        """"""
        gtk.VBox.__init__(self)
        
        self.config = config_parser
        self.settings_list = [] #a list with the settings instances called. Used for polymorphism
        
        #containers-separators.
        vbox1 = gtk.VBox(False, 10) #gtk.VBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio vertical entre hijos.
        #vbox1.set_border_width(10) #outside-space

        #left tabs
        self.notebook = Notebook()
        self.notebook.set_tab_pos(gtk.POS_LEFT)
        self.notebook.set_show_border(False)
        #proxy = Proxy()
        #self.settings_list.append(proxy)
        #self.notebook.append_page(proxy, gtk.Label("Connection"))
        connection_tab = ConnectionTab()
        self.settings_list.append(connection_tab)
        self.notebook.append_page(connection_tab, gtk.Label(_("Connection")))
        addons_tab = AddonsTab(addons_list)
        self.settings_list.append(addons_tab)
        self.notebook.append_page(addons_tab, gtk.Label(_("Addons")))
        
        vbox1.pack_start(self.notebook)
        
        #button_done = gtk.Button("Done")
        #button_done.set_size_request(80, 35)
        #button_done.connect("clicked", self.on_close)
        #halign = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment.
        #halign.add(button_done)
        #vbox1.pack_start(halign, False, False)
        
        #self.connect("response", self.on_close)
        #self.vbox.pack_start(vbox1)
        self.pack_start(vbox1)
        self.show_all()
        #self.run()

    def on_load(self):
        """"""
        for setting in self.settings_list: #polymorphism.
            setting.load()
        logger.debug("Preferences loaded.")

    def on_close(self, widget=None, other=None):
        """"""
        for setting in self.settings_list: #polymorphism.
            setting.save()
        logger.debug("Preferences saved.")



