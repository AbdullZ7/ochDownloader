import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.api import api
from core.conf_parser import conf
from core.events import events
import core.cons as cons

from qt.addons import AddonCore

from history import History
from history_gui import HistoryTab


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.name = _("History")
        self.event_id = events.connect(cons.EVENT_DL_COMPLETE, self.trigger)
        self.parent = parent
        self.config = conf
        self.history = History()
        self.history_tab = HistoryTab(self.history)
    
    def set_menu_item(self):
        pass
        #WIDGET, TITLE, CALLBACK, SENSITIVE = range(4)
        #return (gtk.MenuItem(), _("History"), self.on_history) #can toggle
    
    def get_tab(self):
        return self.history_tab
    
    #def on_history(self, widget):
        #HistoryDlg(self.history, self.parent)
    
    def trigger(self, download_item, *args, **kwargs):
        """"""
        link = download_item.link if download_item.can_copy_link else None
        self.history.set_values(download_item.name, link, download_item.size, download_item.size_complete, download_item.path)
        #remove from the list.
        self.parent.downloads.remove_row(download_item.id)
        del api.complete_downloads[download_item.id]
    
    
