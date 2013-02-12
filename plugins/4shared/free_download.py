#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase

BASE_URL = "http://4shared.com"
WAITING = 0


class PluginDownload(PluginBase):
    def parse(self):
        page = self.get_page(self.link)
        pattern = 'id="btnLink" href="(?P<link>[^"]+)"'
        page = self.click(pattern, page)
        self.countdown('id="downloadDelayTimeSec" class="sec alignCenter light-blue">(?P<count>[^<]+)', page, 320, WAITING)
        pattern = 'href="(?P<link>[^"]+)" class="linkShowD3'
        self.source = self.click(pattern, page, False)