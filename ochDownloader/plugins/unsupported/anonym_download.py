import logging

from core.plugin.base import PluginBase

logger = logging.getLogger(__name__)


class PluginDownload(PluginBase):
    def parse(self):
        self.item.source = self.get_source(self.url)