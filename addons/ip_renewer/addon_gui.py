import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.events import events
from core.conf_parser import conf

from qt.addons import AddonCore

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
        self.name = _("IP renewer")
        self.event_id = None
        self.parent = parent
        self.ip_renewer = IPRenewer()

    def get_preferences(self):
        """"""
        return Preferences()

    def set_menu_item(self):
        """"""
        self.action = self.parent.menu.addAction(self.name, self.on_toggle) #can toggle
        self.action.setCheckable(True)
        if conf.get_addon_option(OPTION_IP_RENEW_ACTIVE, default=False, is_bool=True):
            self.action.setChecked(True)
            self.connect()

    def on_toggle(self):
        if self.action.isChecked(): #se activo
            conf.set_addon_option(OPTION_IP_RENEW_ACTIVE, "True")
            self.connect()
        else:
            conf.set_addon_option(OPTION_IP_RENEW_ACTIVE, "False")
            events.disconnect(cons.EVENT_LIMIT_EXCEEDED, self.event_id)
    
    def connect(self):
        """"""
        self.event_id = events.connect(cons.EVENT_LIMIT_EXCEEDED, self.trigger)
    
    def trigger(self, *args, **kwargs):
        """"""
        #prevent from been garbage collected.
        if not hasattr(self, 'ip_renewer_gui') or not self.ip_renewer_gui.is_working:
            self.ip_renewer_gui = IPRenewerGUI(self.parent, self.ip_renewer)
