import logging
logger = logging.getLogger(__name__)

from core.api import api
from core.conf_parser import conf
from core import events

from qt.addons import AddonCore

from history import History
from history_gui import HistoryTab

#Config parser
OPTION_HISTORY_ACTIVE = "history_active"


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self, parent)
        self.name = _("History")
        self.history = History()
        self.history_tab = HistoryTab(self.history)

    def get_tab(self):
        return self.history_tab

    def set_menu_item(self):
        self.action = self.parent.menu.addAction(self.name, self.on_toggle) #can toggle
        self.action.setCheckable(True)
        if conf.get_addon_option(OPTION_HISTORY_ACTIVE, default=True, is_bool=True):
            self.action.setChecked(True)
            self.connect()

    def on_toggle(self):
        if self.action.isChecked(): #se activo
            conf.set_addon_option(OPTION_HISTORY_ACTIVE, "True")
            self.connect()
        else:
            conf.set_addon_option(OPTION_HISTORY_ACTIVE, "False")
            events.download_complete.disconnect(self.trigger)

    def connect(self):
        """"""
        events.download_complete.connect(self.trigger)
    
    #def on_history(self, widget):
        #HistoryDlg(self.history, self.parent)
    
    def trigger(self, download_item, *args, **kwargs):
        """"""
        link = download_item.link if download_item.can_copy_link else None
        self.history.set_values(download_item.name, link, download_item.size, download_item.size_complete, download_item.path)
        #remove from the list.
        self.parent.downloads.remove_row(download_item.id)
        del api.complete_downloads[download_item.id]
    
    
