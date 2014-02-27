import os
import pkgutil
import logging
from configparser import RawConfigParser

from core import const

logger = logging.getLogger(__name__)

SECTION_MAIN = "main"
OPTION_SLOTS_LIMIT = "slots_limit"
OPTION_PREMIUM = "premium"
OPTION_FREE = "free"

services_dict = {}


class _PluginConfig(RawConfigParser):

    def __init__(self, path):
        super().__init__()
        self.load(path)

    def load(self, path):
        try:
            self.read(path, encoding='utf-8')
        except Exception as err:
            logger.exception(err)

    def get_premium_available(self):
        return self.getboolean(SECTION_MAIN, OPTION_PREMIUM, fallback=False)

    def get_free_available(self):
        return self.getboolean(SECTION_MAIN, OPTION_FREE, fallback=False)
    
    def get_slots_limit(self):
        return self.getint(SECTION_MAIN, OPTION_SLOTS_LIMIT, fallback=1)


def load():
    global services_dict

    for module_loader, plugin, ispkg in pkgutil.iter_modules(path=[const.PLUGINS_PATH, ]):
        if not ispkg:
            continue

        path = os.path.join(const.PLUGINS_PATH, plugin, const.PLUGIN_CONFIG_FILE)
        host = plugin.replace('_', '.')
        services_dict[host] = _PluginConfig(path)

load()