#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        #todo: emit event to popup a format/quality choise window.
        pass


if __name__ == "__main__":
    pass

