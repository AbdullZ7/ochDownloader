import gtk
import pygtk

import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from general import General
from proxy import Proxy


class ConnectionTab(gtk.ScrolledWindow): #gtk.VBox):
    """"""
    def __init__(self):
        #gtk.VBox.__init__(self, False)
        #self.set_border_width(10)
        gtk.ScrolledWindow.__init__(self)
        
        self.settings_list = []
        
        #scroll = gtk.ScrolledWindow()
        self.set_shadow_type(gtk.SHADOW_NONE)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        general = General()
        proxy = Proxy()
        
        self.settings_list.append(general)
        self.settings_list.append(proxy)
        
        vbox1 = gtk.VBox(False, 10)
        vbox1.set_border_width(10)
        vbox1.pack_start(general, False, False)
        vbox1.pack_start(proxy, False, False)
        
        view_port = gtk.Viewport()
        view_port.set_shadow_type(gtk.SHADOW_NONE)
        view_port.add(vbox1)
        
        self.add(view_port)
        
        #self.pack_start(scroll)
    
    def load(self):
        """"""
        for setting in self.settings_list: #polymorphism.
            setting.load()
    
    def save(self):
        """"""
        for setting in self.settings_list: #polymorphism.
            setting.save()



