#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore


class PluginDownload(PluginsCore):
    def parse(self):
        self.source = self.get_page(self.link, default=None, close=False)
