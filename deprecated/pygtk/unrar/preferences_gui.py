import sys
import os
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

from core.config import config_parser
import core.cons as cons

from passwords_handler import passwords_handler


PWD_FILE_PATH = os.path.join(cons.APP_PATH, "pwd.txt")


class Preferences(gtk.VBox):
    """"""
    def __init__(self):
        """"""
        gtk.VBox.__init__(self)
        
        frame = gtk.Frame(_("Passwords (one per line):"))
        
        self.text_field = gtk.TextView()
        self.text_field.set_editable(True)

        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_border_width(10)
        
        scroll.add(self.text_field)
        
        frame.add(scroll)
        
        self.load_pwd()
        
        self.pack_start(frame, True)

    def load_pwd(self):
        """"""
        pwd_set = passwords_handler.get_passwords()
        lines = "\n".join(pwd_set)
        
        if lines:
            buffer = self.text_field.get_buffer()
            buffer.set_text(lines)

    def load(self):
        """"""
        self.load_pwd()

    def save(self):
        """"""
        buffer = self.text_field.get_buffer()
        bounds = buffer.get_bounds()
        txt = buffer.get_text(bounds[0], bounds[1])
        passwords_handler.replace(txt.splitlines())





