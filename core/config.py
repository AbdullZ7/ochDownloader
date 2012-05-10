import os
import threading
import pickle
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError

#Libs
import cons


#main section
SECTION_MAIN = "main"

#main options
OPTION_VERSION = "version"
OPTION_CLIPBOARD_ACTIVE = "clipboard_active"

#network section
SECTION_NETWORK = "network"

#network options
#OPTION_PROXY_TYPE = http
OPTION_PROXY_ACTIVE = "proxy_active"
OPTION_PROXY_IP = "proxy_ip"
OPTION_PROXY_PORT = "proxy_port"
OPTION_PROXY_TYPE = "proxy_type"
OPTION_RETRIES_LIMIT = "retries_limit"

#gui section
SECTION_GUI = "gui"

#gui options
OPTION_WINDOW_SETTINGS = "windows_settings"
OPTION_COLUMNS_WIDTH = "columns_width"
OPTION_SAVE_DL_PATHS = "save_dl_paths"

#addons section
SECTION_ADDONS = "addons"


DEFAULT = {SECTION_MAIN: {OPTION_VERSION: cons.APP_VER, OPTION_CLIPBOARD_ACTIVE: "True"},
                    SECTION_NETWORK: {OPTION_PROXY_TYPE: cons.PROXY_HTTP, OPTION_PROXY_IP: "", OPTION_PROXY_PORT: "0", OPTION_PROXY_ACTIVE: "False", OPTION_RETRIES_LIMIT: "99"},
                    SECTION_GUI: {OPTION_WINDOW_SETTINGS: "-1,-1,-1,-1", OPTION_SAVE_DL_PATHS: pickle.dumps([]), OPTION_COLUMNS_WIDTH: "-1, -1, -1, -1, -1, -1, -1"}, 
                    SECTION_ADDONS: {}
                    }


#thread safety
_thread_lock = threading.RLock()

#decorator
def exception_handler(func):
    #@functools.wraps(func) #accurate debugging
    def wrapper(*args, **kwargs):
        try:
            with _thread_lock:
                func(*args, **kwargs)
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
    return wrapper


class _Config(SafeConfigParser):
    """
    Thread safe.
    when saving (def set_option()) strings do value.replace('%', '%%') to avoid interpolation errors.
    """
    def __init__(self):
        """"""
        SafeConfigParser.__init__(self)
        try:
            self.read(cons.CONFIG_FILE) #read config file
        except Exception as err:
            logger.info(err)
        self.create_config()
        logger.debug("config parser instanced.")
    
    def create_config(self):
        """"""
        for section, options in DEFAULT.items():
            if not self.has_section(section):
                self.add_section(section)
            for option, value in options.items():
                if not self.has_option(section, option):
                    self.set(section, option, value)
        #self.save_config()
  
    def save_config(self):
        """"""
        try:
            with _thread_lock:
                with open(cons.CONFIG_FILE, "wb", cons.FILE_BUFSIZE) as fh:
                    self.write(fh)
        except Exception as  err:
            logger.exception(err)
    
    @exception_handler
    def set_addon_option(self, option, value):
        """"""
        self.set(SECTION_ADDONS, option, value)
    
    def get_addon_option(self, option, default=None, is_bool=False):
        """"""
        try:
            if is_bool:
                return self.getboolean(SECTION_ADDONS, option)
            else:
                return self.get(SECTION_ADDONS, option)
        except (NoSectionError, NoOptionError) as err:
            logger.debug(err)
        except Exception as err:
            logger.exception(err)
        return default

    @exception_handler
    def set_clipboard_active(self, clipboard_active="True"):
        """"""
        self.set(SECTION_MAIN, OPTION_CLIPBOARD_ACTIVE, clipboard_active)

    def get_clipboard_active(self):
        """"""
        try:
            clipboard_active = self.getboolean(SECTION_MAIN, OPTION_CLIPBOARD_ACTIVE)
            return clipboard_active
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return True

    @exception_handler
    def set_proxy_active(self, proxy_active="False"):
        """"""
        self.set(SECTION_NETWORK, OPTION_PROXY_ACTIVE, proxy_active)

    def get_proxy_active(self):
        """"""
        try:
            proxy_active = self.getboolean(SECTION_NETWORK, OPTION_PROXY_ACTIVE)
            return proxy_active
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return False

    @exception_handler
    def set_proxy(self, ptype, ip, port):
        """"""
        self.set(SECTION_NETWORK, OPTION_PROXY_TYPE, ptype)
        self.set(SECTION_NETWORK, OPTION_PROXY_IP, ip)
        self.set(SECTION_NETWORK, OPTION_PROXY_PORT, port)
    
    def get_proxy(self): #proxy_dict
        """"""
        try:
            ptype = self.get(SECTION_NETWORK, OPTION_PROXY_TYPE)
            ip = self.get(SECTION_NETWORK, OPTION_PROXY_IP)
            port = self.getint(SECTION_NETWORK, OPTION_PROXY_PORT)
            return (ptype, ip, port)
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return None

    @exception_handler
    def set_retries_limit(self, limit):
        """"""
        self.set(SECTION_NETWORK, OPTION_RETRIES_LIMIT, limit)
    
    def get_retries_limit(self):
        """"""
        try:
            limit = self.getint(SECTION_NETWORK, OPTION_RETRIES_LIMIT)
            return limit
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return 99

    
    #//////////////////////// [GUI] ////////////////////////
    
    @exception_handler
    def set_window_settings(self, x, y, w, h):
        """"""
        self.set(SECTION_GUI, OPTION_WINDOW_SETTINGS, "{0},{1},{2},{3}".format(x, y, w, h))

    def get_window_settings(self):
        """"""
        try:
            tmp = self.get(SECTION_GUI, OPTION_WINDOW_SETTINGS)
            x, y, w, h = tmp.split(",")
            x, y, w, h = int(x), int(y), int(w), int(h)
            return x, y, w, h
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return -1, -1, -1, -1
    
    @exception_handler
    def set_columns_width(self, columns):
        """"""
        self.set(SECTION_GUI, OPTION_COLUMNS_WIDTH, "{0},{1},{2},{3},{4},{5},{6}".format(*columns))
    
    def get_columns_width(self):
        """"""
        try:
            tmp = self.get(SECTION_GUI, OPTION_COLUMNS_WIDTH)
            columns = tuple([int(width) for width in tmp.split(",")])
            return columns
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return None
    
    @exception_handler
    def set_save_dl_paths(self, paths_list):
        """"""
        self.set(SECTION_GUI, OPTION_SAVE_DL_PATHS, pickle.dumps(paths_list))
    
    def get_save_dl_paths(self):
        """"""
        try:
            paths_list = pickle.loads(self.get(SECTION_GUI, OPTION_SAVE_DL_PATHS))
            return paths_list
        except (NoSectionError, NoOptionError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)
        return []


#modules are singletons in python :)
config_parser = _Config() #make it global.

    
if __name__ == "__main__":
    pass
    
