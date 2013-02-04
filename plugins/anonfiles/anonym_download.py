#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase

BASE_URL = "http://anonfiles.com"


class PluginDownload(PluginBase):
    def parse(self):
        page = self.get_page(self.link)
        s_pattern = 'href="(?P<link>[^"]+)" class="download_button'
        self.source = self.click(s_pattern, page, False)
