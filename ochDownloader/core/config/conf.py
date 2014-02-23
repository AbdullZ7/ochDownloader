import threading
import functools
import logging
from configparser import RawConfigParser

from .const import *


logger = logging.getLogger(__name__)

_rlock = threading.RLock()


# decorator
def rlock(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with _rlock:
            return func(*args, **kwargs)

    return wrapper


class _Config(RawConfigParser):

    def __init__(self):
        super().__init__()
        self.load()
        self.create()

    def load(self):
        try:
            self.read(cons.CONFIG_FILE, encoding='utf-8')
        except Exception as err:
            logger.exception(err)

    def create(self):
        for section, options in list(DEFAULT.items()):
            if not self.has_section(section):
                self.add_section(section)

            for option, value in list(options.items()):
                if not self.has_option(section, option):
                    self.set(section, option, value)

    def save(self):
        try:
            with open(cons.CONFIG_FILE, "w", encoding='utf-8') as fh:
                self.write(fh)
        except Exception as err:
            logger.exception(err)

    @rlock
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @rlock
    def getboolean(self, *args, **kwargs):
        return super().getboolean(*args, **kwargs)

    @rlock
    def getint(self, *args, **kwargs):
        return super().getint(*args, **kwargs)

    @rlock
    def set(self, section, option, value=None):
        super().set(section, option, value)

    def setboolean(self, section, option, value):
        value = "True" if value else "False"
        self.set(section, option, value)

    def setint(self, section, option, value):
        self.set(section, option, str(value))

    def set_addon_option(self, option, value, is_bool=False):
        if is_bool:
            self.setboolean(SECTION_ADDONS, option, value)
        else:
            self.set(SECTION_ADDONS, option, value)

    def get_addon_option(self, option, default=None, is_bool=False):
        if is_bool:
            return self.getboolean(SECTION_ADDONS, option, fallback=default)
        else:
            return self.get(SECTION_ADDONS, option, fallback=default)

    # TODO: Clipboard is an addon, remove this
    def set_clipboard_active(self, active):
        self.setboolean(SECTION_MAIN, OPTION_CLIPBOARD_ACTIVE, active)

    def get_clipboard_active(self):
        return self.getboolean(SECTION_MAIN, OPTION_CLIPBOARD_ACTIVE)

    # Network

    def set_proxy_active(self, active):
        self.setboolean(SECTION_NETWORK, OPTION_PROXY_ACTIVE, active)

    def get_proxy_active(self):
        return self.getboolean(SECTION_NETWORK, OPTION_PROXY_ACTIVE)

    def set_proxy(self, ptype, ip, port):
        self.set(SECTION_NETWORK, OPTION_PROXY_TYPE, ptype)
        self.set(SECTION_NETWORK, OPTION_PROXY_IP, ip)
        self.setint(SECTION_NETWORK, OPTION_PROXY_PORT, port)

    def get_proxy(self):
        ptype = self.get(SECTION_NETWORK, OPTION_PROXY_TYPE)
        ip = self.get(SECTION_NETWORK, OPTION_PROXY_IP)
        port = self.getint(SECTION_NETWORK, OPTION_PROXY_PORT)
        return ptype, ip, port

    def set_retries_limit(self, limit):
        self.setint(SECTION_NETWORK, OPTION_RETRIES_LIMIT, limit)

    def get_retries_limit(self):
        return self.getint(SECTION_NETWORK, OPTION_RETRIES_LIMIT)

    def set_html_dl(self, active):
        self.setboolean(SECTION_NETWORK, OPTION_HTML_DL, active)

    def get_html_dl(self):
        return self.getboolean(SECTION_NETWORK, OPTION_HTML_DL)

    def set_max_conn(self, max):
        self.setint(SECTION_NETWORK, OPTION_MAX_CONN, max)

    def get_max_conn(self):
        return self.getint(SECTION_NETWORK, OPTION_MAX_CONN)

    # GUI

    def set_window_settings(self, x, y, w, h):
        self.set(SECTION_GUI, OPTION_WINDOW_SETTINGS, json.dumps([x, y, w, h]))

    def get_window_settings(self):
        values = self.get(SECTION_GUI, OPTION_WINDOW_SETTINGS)
        return tuple(json.loads(values))

    def set_save_dl_paths(self, path_list):
        self.set(SECTION_GUI, OPTION_SAVE_DL_PATHS, json.dumps(path_list))

    def get_save_dl_paths(self):
        paths = self.get(SECTION_GUI, OPTION_SAVE_DL_PATHS)
        return json.loads(paths)

    def set_tray_available(self, active):
        self.setboolean(SECTION_GUI, OPTION_TRAY_ICON, active)

    def get_tray_available(self):
        return self.getboolean(SECTION_GUI, OPTION_TRAY_ICON)

    def set_auto_switch_tab(self, active):
        self.setboolean(SECTION_GUI, OPTION_SWITCH_TAB, active)

    def get_auto_switch_tab(self):
        return self.getboolean(SECTION_GUI, OPTION_SWITCH_TAB)


conf = _Config()