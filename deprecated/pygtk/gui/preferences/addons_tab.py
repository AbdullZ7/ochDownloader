import gtk
import pygtk

import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import core.cons as cons

from gui.notebook_gui import Notebook


class AddonsTab(gtk.ScrolledWindow):
    """"""
    def __init__(self, addons_list):
        #gtk.VBox.__init__(self, False)
        #self.set_border_width(10)
        gtk.ScrolledWindow.__init__(self)
        
        self.settings_list = []
        
        #scroll = gtk.ScrolledWindow()
        self.set_shadow_type(gtk.SHADOW_NONE)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        #general = General()
        #proxy = Proxy()
        
        #self.settings_list.append(general)
        
        notebook = Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.set_show_border(False)
        
        for addon in addons_list:
            addon_preferences = addon.get_preferences()
            if addon_preferences is not None:
                notebook.append_page(self.inside_tabs(addon_preferences), gtk.Label(addon.name))
                self.settings_list.append(addon_preferences)
        
        vbox1 = gtk.VBox(False, 10)
        vbox1.set_border_width(10)
        vbox1.pack_start(notebook, True, True)
        #vbox1.pack_start(proxy, False, False)
        
        view_port = gtk.Viewport()
        view_port.set_shadow_type(gtk.SHADOW_NONE)
        view_port.add(vbox1)
        
        self.add(view_port)
        
        #self.pack_start(scroll)
    
    def inside_tabs(self, addon_preferences):
        """"""
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_shadow_type(gtk.SHADOW_NONE)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox1 = gtk.VBox(False, 10)
        vbox1.set_border_width(10)
        vbox1.pack_start(addon_preferences, True)
        view_port = gtk.Viewport()
        view_port.set_shadow_type(gtk.SHADOW_NONE)
        view_port.add(vbox1)
        scrolled_window.add(view_port)
        return scrolled_window

    def load(self):
        """"""
        for setting in self.settings_list: #polymorphism.
            setting.load()

    def save(self):
        """"""
        for setting in self.settings_list: #polymorphism.
            setting.save()