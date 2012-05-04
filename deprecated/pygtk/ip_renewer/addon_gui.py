import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

import core.cons as cons
from core.events import events
from core.config import config_parser

from gui.addons_gui import AddonCore

from preferences_gui import Preferences
from ip_renewer import IPRenewer
from ip_renewer_gui import IPRenewerGUI


#Config parser
OPTION_IP_RENEW_ACTIVE = "ip_renew_active"
OPTION_IP_RENEW_SCRIPT_PATH = "ip_renew_script_path"
OPTION_RENEW_SCRIPT_ACTIVE = "renew_script_active"


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.name = _("IP Renewer")
        self.event_id = None
        self.parent = parent
        #self.rlock = threading.RLock()
        self.ip_renewer_cls = IPRenewer()

    def get_preferences(self):
        """"""
        return Preferences()

    def get_menu_item(self):
        """"""
        WIDGET, TITLE, CALLBACK, SENSITIVE = range(4)
        config_change_ip = (gtk.CheckMenuItem(), self.name, self.on_change_ip) #can toggle
        if config_parser.get_addon_option(OPTION_IP_RENEW_ACTIVE, default=False, is_bool=True):
            config_change_ip[WIDGET].set_active(True)
            self.connect()
        return config_change_ip

    def on_change_ip(self, widget):
        if widget.get_active(): #se activo
            config_parser.set_addon_option(OPTION_IP_RENEW_ACTIVE, "True")
            self.connect()
        else:
            config_parser.set_addon_option(OPTION_IP_RENEW_ACTIVE, "False")
            events.disconnect(cons.EVENT_LIMIT_EXCEEDED, self.event_id)
    
    def connect(self):
        """"""
        self.event_id = events.connect(cons.EVENT_LIMIT_EXCEEDED, self.trigger, self.parent)
    
    def trigger(self, parent, *args, **kwargs):
        """"""
        if not self.ip_renewer_cls.is_alive():
            change_ip = IPRenewerGUI(parent, self.ip_renewer_cls)
