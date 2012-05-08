#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore

#CONNECTION_RETRY = 3
WAITING = 50


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        if "/video/" in self.link:
            self.link = self.link.replace("/video/", "/download/")
        elif "/audio/" in self.link:
            self.link = self.link.replace("/audio/", "/download/")
        elif "/image/" in self.link:
            self.link = self.link.replace("/image/", "/download/")
        link = self.link
        page = self.get_page(link, form={"download": 1})
        m_pattern = 'link_enc=new Array\(\'(?P<link>.*?)\'\);'
        m = self.get_match(m_pattern, page)
        if m is not None:
            link_file = "".join(m.group('link').split("','")) #url = h', 't', 't', 'p', ...
            if not self.wait_func(WAITING):
                self.source = self.get_page(link_file, close=False)
        else: #link not found
            pass


if __name__ == "__main__":
    pass
