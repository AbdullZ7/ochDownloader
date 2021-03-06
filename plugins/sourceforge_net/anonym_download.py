#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase


class PluginDownload(PluginBase):
    def parse(self):
        page = self.get_page(self.link)
        m = self.get_match('; url=(?P<link>[^"]+)', page, "Link not found")
        http_link = m.group('link').replace("&amp;", "&")
        self.source = self.get_page(http_link, close=False)