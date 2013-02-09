import logging
logger = logging.getLogger(__name__)

from core import events
from core.config import conf

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
        AddonCore.__init__(self, parent)
        self.name = _("IP renewer")
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
            events.limit_exceeded.disconnect(self.trigger)
    
    def connect(self):
        """"""
        events.limit_exceeded.connect(self.trigger)
    
    def trigger(self, *args, **kwargs):
        """"""
        #prevent from been garbage collected.
        if not hasattr(self, 'ip_renewer_gui') or not self.ip_renewer_gui.is_working:
            self.ip_renewer_gui = IPRenewerGUI(self.parent, self.ip_renewer)
