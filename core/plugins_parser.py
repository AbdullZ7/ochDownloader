import os
import pkgutil
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError

#Libs
import cons


#main section
SECTION_MAIN = "main"

#main options
OPTION_SLOTS_LIMIT = "slots_limit"
OPTION_PREMIUM = "premium"
OPTION_CAPTCHA_REQUIRED = "captcha_required"


DEFAULT = {SECTION_MAIN: {OPTION_SLOTS_LIMIT: "1",
                          OPTION_PREMIUM: "False",
                          OPTION_CAPTCHA_REQUIRED: "False"},
                        }


class _PluginsParser:
    """"""
    def __init__(self):
        """"""
        self.services_dict = {}
        try:
            for module_loader, plugin, ispkg in pkgutil.iter_modules(path=[cons.PLUGINS_PATH, ]):
                file_path = os.path.join(cons.PLUGINS_PATH, plugin, cons.PLUGIN_CONFIG_FILE)
                self.services_dict[plugin] = _PluginsConfig(file_path)
        except Exception as err:
            logger.exception(err)
        logger.debug("plugin parser instanced.")
    
    def get_plugin_item(self, plugin): #plugin = host
        """"""
        try:
            return self.services_dict[plugin]
        except KeyError:
            file_path = os.path.join(cons.PLUGINS_PATH, plugin, cons.PLUGIN_CONFIG_FILE)
            plugin_config = _PluginsConfig(file_path)
            self.services_dict[plugin] = plugin_config
            return plugin_config


class _PluginsConfig(SafeConfigParser):
    """
    when saving (def set_option()) strings do value.replace('%', '%%') to avoid interpolation errors.
    """
    def __init__(self, file_path):
        """"""
        SafeConfigParser.__init__(self)
        try:
            self.read(file_path) #read config file
        except Exception as err:
            logger.info(err)
        self.create_config()
    
    def create_config(self):
        """"""
        for section, options in DEFAULT.items():
            if not self.has_section(section):
                self.add_section(section)
            for option, value in options.items():
                if not self.has_option(section, option):
                    self.set(section, option, value)
        #self.save_config()

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
    
    def get_captcha_required(self):
        """"""
        try:
            required = self.getboolean(SECTION_MAIN, OPTION_CAPTCHA_REQUIRED)
            return required
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return False


#modules are singletons in python :)
plugins_parser = _PluginsParser() #make it global.
