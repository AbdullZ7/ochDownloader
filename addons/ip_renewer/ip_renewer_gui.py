import logging
logger = logging.getLogger(__name__)

import core.cons as cons
from core.api import api
from core.conf_parser import conf

from qt.signals import signals

#Config parser
OPTION_IP_RENEW_ACTIVE = "ip_renew_active"
OPTION_RENEW_SCRIPT_ACTIVE = "renew_script_active"


class IPRenewerGUI:
    """"""
    def __init__(self, parent, ip_renewer):
        """"""
        self.ip_renewer = ip_renewer
        self.parent = parent
        
        self.id_item_list = []
        self.is_working = True

        if self.can_change_ip():
            self.id_item_list = [download_item.id for download_item in api.get_active_downloads().values() + api.get_queue_downloads().values()]
            signals.on_stop_all.emit()
            if conf.get_addon_option(OPTION_RENEW_SCRIPT_ACTIVE, default=False, is_bool=True):
                self.ip_renewer.start_shell_script()
            else:
                self.ip_renewer.start_default_ip_renew()
            
            self.status_msg = _("Changing IP...")
            signals.status_bar_push_msg.emit(self.status_msg)
            
            self.timer = self.parent.idle_timeout(1000, self.update)
        else:
            self.is_working = False
    
    def can_change_ip(self):
        """"""
        for download_item in api.get_active_downloads().itervalues():
            #p = plugins_parser.get_plugin_item(download_item.host)
            if not download_item.can_resume and download_item.time: # or (p.get_captcha_required() and not download_item.is_premium and download_item.time):
                return False
        return True
    
    def update(self):
        """"""
        if not self.ip_renewer.is_running():
            signals.status_bar_pop_msg.emit(self.status_msg)
            for id_item in self.id_item_list:
                api.start_download(id_item)
                try:
                    self.parent.downloads.rows_buffer[id_item][1] = self.parent.downloads.icons_dict[cons.STATUS_QUEUE]
                except Exception as err:
                    logger.debug(err)
            self.timer.stop()
            self.is_working = False