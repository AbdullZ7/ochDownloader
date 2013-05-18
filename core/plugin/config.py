import os
import pkgutil
import logging
logger = logging.getLogger(__name__)
from ConfigParser import RawConfigParser, NoSectionError, NoOptionError

#Libs
from core import cons

#main section
SECTION_MAIN = "main"

#main options
OPTION_SLOTS_LIMIT = "slots_limit"
OPTION_PREMIUM = "premium"
OPTION_FREE = "free"


DEFAULT = {SECTION_MAIN: {OPTION_SLOTS_LIMIT: "1",
                          OPTION_PREMIUM: "False",
                          OPTION_FREE: "False"},
                        }


class _PluginsConfigLoader:
    """"""
    def __init__(self):
        """"""
        self.services_dict = {}
        self.load_plugins_config()
        logger.debug("plugin parser instanced.")

    def load_plugins_config(self):
        try:
            for module_loader, plugin, ispkg in pkgutil.iter_modules(path=[cons.PLUGINS_PATH, ]):
                path = os.path.join(cons.PLUGINS_PATH, plugin, cons.PLUGIN_CONFIG_FILE)
                plugin = plugin.replace('_', '.')
                self.services_dict[plugin] = _PluginConfig(path)
        except Exception as err:
            logger.exception(err)

    def get_plugin_item(self, plugin): #plugin = host
        """"""
        try:
            return self.services_dict[plugin]
        except KeyError:
            path = os.path.join(cons.PLUGINS_PATH, plugin, cons.PLUGIN_CONFIG_FILE)
            plugin_config = _PluginConfig(path)
            self.services_dict[plugin] = plugin_config
            return plugin_config


class _PluginConfig(RawConfigParser):
    """"""
    def __init__(self, path):
        """"""
        RawConfigParser.__init__(self)
        self.load(path)
        self.create()

    def load(self, path):
        try:
            self.read(path)  # read config file
        except Exception as err:
            logger.warning(err)

    def create(self):
        """"""
        for section, options in DEFAULT.items():
            if not self.has_section(section):
                self.add_section(section)
            for option, value in options.items():
                if not self.has_option(section, option):
                    self.set(section, option, value)

    def get_premium_available(self):
        """"""
        try:
            premium_available = self.getboolean(SECTION_MAIN, OPTION_PREMIUM)
            return premium_available
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return False

    def get_free_available(self):
        """"""
        try:
            free_available = self.getboolean(SECTION_MAIN, OPTION_FREE)
            return free_available
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return False
    
    def get_slots_limit(self):
        """"""
        try:
            limit = self.getint(SECTION_MAIN, OPTION_SLOTS_LIMIT)
            return limit
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return 1


plugins_config = _PluginsConfigLoader()
