#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        link = self.link
        page = self.get_page(link, form={"download": "Regular Download"})
        self.source = self.click('download_button" href="(?P<link>[^"]+)', page, False)


if __name__ == "__main__":
    pass
