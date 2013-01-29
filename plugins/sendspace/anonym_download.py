#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore


class PluginDownload(PluginsCore):
    def parse(self):
        link = self.link
        page = self.get_page(link, form={"download": "Regular Download"})
        self.source = self.click('download_button" href="(?P<link>[^"]+)', page, False)


if __name__ == "__main__":
    pass
