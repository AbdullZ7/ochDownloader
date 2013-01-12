#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore

BASE_URL = "http://anonfiles.com"


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        page = self.get_page(self.link)
        s_pattern = 'href="(?P<link>[^"]+)" class="download_button'
        self.source = self.click(s_pattern, page, False)
