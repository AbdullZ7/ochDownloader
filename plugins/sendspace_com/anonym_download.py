#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase


class PluginDownload(PluginBase):
    def parse(self):
        link = self.link
        page = self.get_page(link, form={"download": "Regular Download"})
        self.source = self.click('download_button" href="(?P<link>[^"]+)', page, False)


if __name__ == "__main__":
    pass
