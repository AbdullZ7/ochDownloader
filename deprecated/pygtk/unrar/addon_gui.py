import threading
import time
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

import core.cons as cons
from core.events import events
from core.conf_parser import conf
from core.idle_queue import register_event, remove_event

from gui.addons_gui import AddonCore

from preferences_gui import Preferences
from unrar_gui import UnRARGUI
from passwords_handler import passwords_handler #init singleton


#Config parser
OPTION_UNRAR_ACTIVE = "unrar_active"


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.name = _("Auto Extraction")
        self.event_id = None
        self.parent = parent
        self.lock = threading.Lock()
        self.widgets_list = []
        events.connect(cons.EVENT_PASSWORD, passwords_handler.add)
        #self.ip_renewer_cls = IPRenewer()

    def get_preferences(self):
        """"""
        return Preferences()

    def save(self):
        """"""
        passwords_handler.save()

    def get_menu_item(self):
        """"""
        WIDGET, TITLE, CALLBACK, SENSITIVE = range(4)
        config_unrar = (gtk.CheckMenuItem(), self.name, self.on_unrar) #can toggle
        if conf.get_addon_option(OPTION_UNRAR_ACTIVE, default=False, is_bool=True):
            config_unrar[WIDGET].set_active(True)
            self.connect()
        return config_unrar

    def on_unrar(self, widget):
        if widget.get_active(): #se activo
            conf.set_addon_option(OPTION_UNRAR_ACTIVE, "True")
            self.connect()
        else:
            conf.set_addon_option(OPTION_UNRAR_ACTIVE, "False")
            events.disconnect(cons.EVENT_DL_COMPLETE, self.event_id)
    
    def connect(self):
        """"""
        self.event_id = events.connect(cons.EVENT_DL_COMPLETE, self.trigger)
    
    def trigger(self, *args, **kwargs):
        """
        DONE: Esperar a que termine o terminar al salir del programa.
        """
        th = threading.Thread(group=None, target=self.unrar_thread, name=None, args=args)
        th.daemon = True #exit even if the thread is alive.
        th.start()
    
    def unrar_thread(self, *args):
        """"""
        with self.lock:
            event = threading.Event()
            gobject.idle_add(self.unrar, event, *args)
            if register_event(event): #set() event on exit app.
                event.wait() #wait for set().
                remove_event(event)
    
    def unrar(self, event, download_item, *args):
        """"""
        unrar_gui = UnRARGUI(event, download_item, self.parent, self.widgets_list)
        if not unrar_gui.is_extracting: #wont extract
            event.set()
        return False
