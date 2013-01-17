#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore, ParsingError


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        page = self.get_page(self.link)
        m = self.get_match('; url=(?P<link>[^"]+)', page)
        if m is not None:
            http_link = m.group('link').replace("&amp;", "&")
            self.source = self.get_page(http_link, close=False)
        else:
            raise ParsingError('Link not found.')