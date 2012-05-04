import gtk
import pygtk

import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import core.cons as cons
from core.config import config_parser


class General(gtk.Frame):
    """"""
    def __init__(self):
        """"""
        gtk.Frame.__init__(self, _("General:"))
        
        vbox_general = gtk.VBox(False, 10)
        vbox_general.set_border_width(10)
        hbox_retries = gtk.HBox(False, 10)
        
        label_retries = gtk.Label(_("Retries limit:"))
        
        hbox_retries.pack_start(label_retries, False, False)
        self.spin_retries = gtk.SpinButton(None, 1, 0)
        self.spin_retries.set_property("shadow-type", gtk.SHADOW_NONE)
        self.spin_retries.set_range(0, 100000)
        self.spin_retries.set_increments(1, 1)
        self.spin_retries.set_numeric(True)
        self.spin_retries.set_value(config_parser.get_retries_limit())
        hbox_retries.pack_start(self.spin_retries, False, False)
        
        vbox_general.pack_start(hbox_retries, False, False)
        
        self.add(vbox_general)
    
    def load(self):
        """"""
        pass
    
    def save(self):
        """"""
        limit = str(self.spin_retries.get_value_as_int())
        config_parser.set_retries_limit(limit)


