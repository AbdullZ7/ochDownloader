#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase


class PluginDownload(PluginBase):
    def parse(self):
        self.source = self.get_page(self.link, default=None, close=False)
