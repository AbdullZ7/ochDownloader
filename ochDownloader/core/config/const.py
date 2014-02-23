import json

from core import cons


# Main
SECTION_MAIN = "main"
OPTION_VERSION = "version"
OPTION_CLIPBOARD_ACTIVE = "clipboard_active"

# Network
SECTION_NETWORK = "network"
OPTION_PROXY_ACTIVE = "proxy_active"
OPTION_PROXY_IP = "proxy_ip"
OPTION_PROXY_PORT = "proxy_port"
OPTION_PROXY_TYPE = "proxy_type"
OPTION_RETRIES_LIMIT = "retries_limit"
OPTION_HTML_DL = "html_download"
OPTION_MAX_CONN = "max_conn"

# GUI
SECTION_GUI = "gui"
OPTION_WINDOW_SETTINGS = "windows_settings"
OPTION_SAVE_DL_PATHS = "save_dl_paths"
OPTION_TRAY_ICON = "tray_icon"
OPTION_SWITCH_TAB = "switch_tab"

# Addons
SECTION_ADDONS = "addons"

# Default values
DEFAULT = {
    SECTION_MAIN: {
        OPTION_VERSION: cons.APP_VER,
        OPTION_CLIPBOARD_ACTIVE: "True"
    },
    SECTION_NETWORK: {
        OPTION_PROXY_TYPE: cons.PROXY_HTTP,
        OPTION_PROXY_IP: "",
        OPTION_PROXY_PORT: "0",
        OPTION_PROXY_ACTIVE: "False",
        OPTION_RETRIES_LIMIT: "99",
        OPTION_HTML_DL: "False",
        OPTION_MAX_CONN: "5"
    },
    SECTION_GUI: {
        OPTION_WINDOW_SETTINGS: json.dumps([-1, -1, -1, -1]),
        OPTION_SAVE_DL_PATHS: json.dumps([]),
        OPTION_TRAY_ICON: "False",
        OPTION_SWITCH_TAB: "True"
    },
    SECTION_ADDONS: {}
}