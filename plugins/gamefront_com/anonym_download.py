#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase


class PluginDownload(PluginBase):
    def parse(self):
        page = self.get_page(self.link)
        page = self.click('href="(?P<link>[^"]+)" class="downloadNow', page)
        self.source = self.click('downloadUrl = \'(?P<link>[^\']+)', page, False)


if __name__ == "__main__":
    pass