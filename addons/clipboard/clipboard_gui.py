import logging
logger = logging.getLogger(__name__)

from core import utils
from core.config import conf
from core.plugin.config import plugins_config

from PySide.QtGui import *

from qt import signals

#Config parser
OPTION_CLIPBOARD_EXTS = "clipboard_exts"
OPTION_CLIPBOARD_ACTIVE = "clipboard_exts_active"
EXTS = ".exe;.rar;.zip;.avi;.mkv;.mp4;.msi;.mp3;.mka;.flv;.jar;.pdf;.iso"


class Clipboard:
    """"""
    def __init__(self):
        """"""
        self.text_old= ""
        self.len_old = 0
        self.services = self.services()
        self.clipboard = QApplication.clipboard()

    def services(self):
        """"""
        services = plugins_config.services_dict.keys()
        logger.debug("Services: {0}".format(services))
        return services

    def enable(self):
        """"""
        self.clipboard.dataChanged.connect(self.set_links)

    def disable(self):
        """"""
        self.clipboard.dataChanged.disconnect(self.set_links)
    
    def set_links(self):
        text = self.clipboard.text()
        if len(text) != self.len_old or text != self.text_old:
            urls = self.check_supported(self.check_text(text))
            if urls:
                signals.add_downloads_to_check.emit(urls)
                signals.captured_links_count.emit(len(urls))
                if conf.get_auto_switch_tab():
                    signals.switch_tab.emit(1)
            self.len_old = len(text)
            self.text_old = text

    def check_text(self, text):
        urls = []
        if text:
            urls = utils.links_parser(text)
        return urls

    def check_supported(self, urls):
        """"""
        exts_active = conf.get_addon_option(OPTION_CLIPBOARD_ACTIVE, default=True, is_bool=True)
        exts = conf.get_addon_option(OPTION_CLIPBOARD_EXTS) or EXTS #may be an empty str
        exts = tuple(exts.split(";"))
        links = []
        for url in urls:
            if exts_active and exts and url.lower().endswith(exts):
                links.append(url)
            else:
                for name in self.services:
                    if name in url:
                        links.append(url)
                        break
        return links
