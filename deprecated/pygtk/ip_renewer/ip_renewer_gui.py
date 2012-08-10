import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

import core.cons as cons
from core.api import api
from core.conf_parser import conf
from core.plugins_parser import plugins_parser


#Config parser
OPTION_IP_RENEW_ACTIVE = "ip_renew_active"
OPTION_IP_RENEW_SCRIPT_PATH = "ip_renew_script_path"
OPTION_RENEW_SCRIPT_ACTIVE = "renew_script_active"


class IPRenewerGUI:
    """"""
    def __init__(self, parent, ip_renewer_cls):
        """"""
        self.id_list = []
        
        self.stop_all = parent.downloads_list_gui.on_stop_all
        
        if self.can_change_ip():
            self.pending_events()
            self.id_list = [download_item.id for download_item in api.get_active_downloads().values() + api.get_queue_downloads().values()]
            self.pending_events()
            self.stop_all()
            self.pending_events()
            self.change_ip_th = ip_renewer_cls
            if conf.get_addon_option(OPTION_RENEW_SCRIPT_ACTIVE, default=False, is_bool=True):
                self.change_ip_th.start(conf.get_addon_option(OPTION_IP_RENEW_SCRIPT_PATH, default=""))
            else:
                self.change_ip_th.start()
            gobject.timeout_add(1000, self.update_status, parent)
            self.msg_id = parent.status_bar.push_msg(_("Changing IP..."))
    
    def can_change_ip(self):
        """"""
        for download_item in api.get_active_downloads().itervalues():
            p = plugins_parser.get_plugin_item(download_item.host)
            if (not download_item.can_resume and download_item.time): # or (p.get_captcha_required() and not download_item.is_premium and download_item.time):
                return False
        return True
    
    def update_status(self, parent):
        """"""
        if not self.change_ip_th.is_alive():
            parent.status_bar.pop_msg(self.msg_id)
            self.pending_events()
            for id_item in self.id_list:
                parent.download_manager.start_download(id_item)
                try:
                    parent.downloads_list_gui.rows_buffer[id_item][1] = parent.downloads_list_gui.icons_dict[cons.STATUS_QUEUE]
                except Exception as err:
                    logger.debug(err)
            return False #stop updating.
        return True
    
    def pending_events(self):
        """
        Avoid gui hanging.
        """
        while gtk.events_pending():
            gtk.main_iteration(False)

