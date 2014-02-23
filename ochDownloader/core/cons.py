import os
import sys

# App
APP_NAME = "ochDownloader"
APP_VER = "0.9.2"
APP_TITLE = " ".join((APP_NAME, APP_VER, ""))

# App paths
APP_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "")
HOME_PATH = os.path.expanduser("~")
HOME_APP_PATH = os.path.join(HOME_PATH, "." + APP_NAME)  # hidden folder .ochDownloader
DLFOLDER_PATH = os.path.join(HOME_PATH, "Downloads")
PLUGINS_PATH = os.path.join(APP_PATH, "plugins")
ADDONS_GUI_PATH = os.path.join(APP_PATH, "addons")
MEDIA_PATH = os.path.join(APP_PATH, "media")
LOCALE_PATH = os.path.join(APP_PATH, "Locale")
CONFIG_FILE = os.path.join(HOME_APP_PATH, "settings.cfg")
SESSION_FILE = os.path.join(HOME_APP_PATH, "session3")
DB_PATH = os.path.join(HOME_APP_PATH, "db")
DB_FILE = os.path.join(DB_PATH, "db.sqlite")
IPC_PORT_FILE = os.path.join(HOME_APP_PATH, "port")

# Plugins
PLUGIN_CONFIG_FILE = "settings.cfg"

# File
FILE_BUFSIZE = 1024 * 1024  # 1MB, 0 = no buffer, -1 = OS buffer.

# OS
OS_WIN = False
OS_UNIX = False
OS_OSX = False

if 'win32' in sys.platform.lower():
    OS_WIN = True
elif 'darwin' in sys.platform.lower():
    OS_OSX = True
else:
    OS_UNIX = True

# Logger
LOG_NAME = "error.log"
LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
LOG_MODE = "wb"
LOG_FILE = os.path.join(HOME_APP_PATH, LOG_NAME)

# Update
UPDATE_URL = "http://www.ochdownloader.com/update.txt"
UPDATE_UNIX_URL = "http://www.ochdownloader.com/updateunix.txt"
#UPDATE_PATH = os.path.join(APP_PATH, "update.exe")

# Proxy
PROXY_SOCKS5 = "socks5"
PROXY_SOCKS4 = "socks4"
PROXY_HTTP = "http"

# Status
STATUS_RUNNING = "Running"
STATUS_STOPPED = "Stopped"
STATUS_QUEUE = "Queue"
STATUS_FINISHED = "Finished"
STATUS_ERROR = "Error"

# Link status
LINK_ALIVE = "Alive"
LINK_DEAD = "Dead"
LINK_UNAVAILABLE = "Unavailable"
LINK_ERROR = "Error"
LINK_CHECKING = "Checking"

# Account status
ACCOUNT_PREMIUM = "Premium"
ACCOUNT_FREE = "Free"
ACCOUNT_FAIL = "Fail"  # login fail
ACCOUNT_ERROR = "Error"  # cant connect

# Unavailable names
UNKNOWN = "Unknown"
UNSUPPORTED = "unsupported"

# Download features
DL_RESUME = "can_reconnect"
DL_PREMIUM = "is_premium"