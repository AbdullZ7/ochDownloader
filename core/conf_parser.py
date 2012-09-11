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
OPTION_HTML_DL = "html_download"
OPTION_MAX_CONN = "max_conn"

#gui section
SECTION_GUI = "gui"

#gui options
OPTION_WINDOW_SETTINGS = "windows_settings"
OPTION_COLUMNS_WIDTH = "columns_width"
OPTION_SAVE_DL_PATHS = "save_dl_paths"
OPTION_TRAY_ICON = "tray_icon"

#addons section
SECTION_ADDONS = "addons"


DEFAULT = {SECTION_MAIN: {OPTION_VERSION: cons.APP_VER, OPTION_CLIPBOARD_ACTIVE: "True"},
                    SECTION_NETWORK: {OPTION_PROXY_TYPE: cons.PROXY_HTTP, OPTION_PROXY_IP: "", OPTION_PROXY_PORT: "0",
                                      OPTION_PROXY_ACTIVE: "False", OPTION_RETRIES_LIMIT: "99", OPTION_HTML_DL: "False",
                                      OPTION_MAX_CONN: "10"},
                    SECTION_GUI: {OPTION_WINDOW_SETTINGS: "-1,-1,-1,-1", OPTION_SAVE_DL_PATHS: pickle.dumps([]),
                                  OPTION_COLUMNS_WIDTH: "-1, -1, -1, -1, -1, -1, -1", OPTION_TRAY_ICON: "False"},
                    SECTION_ADDONS: {}
                    }


#thread safety
_thread_lock = threading.RLock()

#decorator
def exception_handler(default=None):
    def decorator(func):
        #@functools.wraps(func) #accurate debugging
        def wrapper(*args, **kwargs):
            try:
                with _thread_lock:
                    return func(*args, **kwargs)
            except Exception as err:
                logger.exception(err)
                return default
        return wrapper
    return decorator


class _Config(SafeConfigParser):
    """
    Thread safe.
    when saving (def set_option()) strings do value.replace('%', '%%') to avoid interpolation errors.
    """
    def __init__(self):
        """"""
        SafeConfigParser.__init__(self)
        self.load()
        self.create_config()
        logger.debug("config parser instanced.")

    def load(self):
        try:
            self.read(cons.CONFIG_FILE)
        except Exception as err:
            logger.warning(err)

    def create_config(self):
        """"""
        for section, options in DEFAULT.items():
            if not self.has_section(section):
                self.add_section(section)
            for option, value in options.items():
                if not self.has_option(section, option):
                    self.set(section, option, value)

    @exception_handler()
    def save(self):
        """"""
        with open(cons.CONFIG_FILE, "wb", cons.FILE_BUFSIZE) as fh:
            self.write(fh)
    
    @exception_handler()
    def set_addon_option(self, option, value):
        """"""
        self.set(SECTION_ADDONS, option, value)

    #@exception_handler(default=...)
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

    @exception_handler()
    def set_clipboard_active(self, clipboard_active="True"):
        """"""
        self.set(SECTION_MAIN, OPTION_CLIPBOARD_ACTIVE, clipboard_active)

    @exception_handler(default=True)
    def get_clipboard_active(self):
        """"""
        return self.getboolean(SECTION_MAIN, OPTION_CLIPBOARD_ACTIVE)

    @exception_handler()
    def set_proxy_active(self, proxy_active="False"):
        """"""
        self.set(SECTION_NETWORK, OPTION_PROXY_ACTIVE, proxy_active)

    @exception_handler(default=False)
    def get_proxy_active(self):
        """"""
        return self.getboolean(SECTION_NETWORK, OPTION_PROXY_ACTIVE)

    @exception_handler()
    def set_proxy(self, ptype, ip, port):
        """"""
        self.set(SECTION_NETWORK, OPTION_PROXY_TYPE, ptype)
        self.set(SECTION_NETWORK, OPTION_PROXY_IP, ip)
        self.set(SECTION_NETWORK, OPTION_PROXY_PORT, port)

    @exception_handler(default=None)
    def get_proxy(self): #proxy_dict
        """"""
        ptype = self.get(SECTION_NETWORK, OPTION_PROXY_TYPE)
        ip = self.get(SECTION_NETWORK, OPTION_PROXY_IP)
        port = self.getint(SECTION_NETWORK, OPTION_PROXY_PORT)
        return ptype, ip, port

    @exception_handler()
    def set_retries_limit(self, limit):
        """"""
        self.set(SECTION_NETWORK, OPTION_RETRIES_LIMIT, limit)

    @exception_handler(default=99)
    def get_retries_limit(self):
        """"""
        return self.getint(SECTION_NETWORK, OPTION_RETRIES_LIMIT)

    @exception_handler()
    def set_html_dl(self, allow):
        """"""
        allow = "True" if allow else "False"
        self.set(SECTION_NETWORK, OPTION_HTML_DL, allow)

    @exception_handler(default=False)
    def get_html_dl(self):
        """"""
        return self.getboolean(SECTION_NETWORK, OPTION_HTML_DL)

    @exception_handler()
    def set_max_conn(self, max):
        self.set(SECTION_NETWORK, OPTION_MAX_CONN, max)

    @exception_handler(default=10)
    def get_max_conn(self):
        return self.getint(SECTION_NETWORK, OPTION_MAX_CONN)

    
    #//////////////////////// [GUI] ////////////////////////

    @exception_handler()
    def set_window_settings(self, x, y, w, h):
        """"""
        self.set(SECTION_GUI, OPTION_WINDOW_SETTINGS, "{0},{1},{2},{3}".format(x, y, w, h))

    @exception_handler(default=(-1, -1, -1, -1))
    def get_window_settings(self):
        """"""
        tmp = self.get(SECTION_GUI, OPTION_WINDOW_SETTINGS)
        x, y, w, h = tmp.split(",")
        x, y, w, h = int(x), int(y), int(w), int(h)
        return x, y, w, h

    @exception_handler()
    def set_columns_width(self, columns):
        """"""
        self.set(SECTION_GUI, OPTION_COLUMNS_WIDTH, "{0},{1},{2},{3},{4},{5},{6}".format(*columns))

    @exception_handler(default=None)
    def get_columns_width(self):
        """"""
        tmp = self.get(SECTION_GUI, OPTION_COLUMNS_WIDTH)
        columns = tuple([int(width) for width in tmp.split(",")])
        return columns

    @exception_handler()
    def set_save_dl_paths(self, paths_list):
        """"""
        self.set(SECTION_GUI, OPTION_SAVE_DL_PATHS, pickle.dumps(paths_list))

    @exception_handler(default=[])
    def get_save_dl_paths(self):
        """"""
        return pickle.loads(self.get(SECTION_GUI, OPTION_SAVE_DL_PATHS))

    @exception_handler()
    def set_tray_available(self, allow):
        """"""
        allow = "True" if allow else "False"
        self.set(SECTION_GUI, OPTION_TRAY_ICON, allow)

    @exception_handler(default=False)
    def get_tray_available(self):
        """"""
        return self.getboolean(SECTION_GUI, OPTION_TRAY_ICON)


#modules are singletons in python :)
conf = _Config() #make it global.


if __name__ == "__main__":
    pass

