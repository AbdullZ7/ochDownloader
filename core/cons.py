import os
import sys


#app constants
APP_NAME = "ochDownloader"
APP_VER = "0.9.0"
APP_TITLE = " ".join((APP_NAME, APP_VER, ""))

#app path constants
APP_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "") #.decode("utf-8") #os.path.dirname(sys.argv[0]) = .../root, os.path.join = .../root/
DLFOLDER_PATH = os.path.join(APP_PATH, "Downloads")
PLUGINS_PATH = os.path.join(APP_PATH, "plugins")
CONFIG_FILE = os.path.join(APP_PATH, "config.ini")
SESSION_FILE = os.path.join(APP_PATH, "session")
ADDONS_GUI_PATH = os.path.join(APP_PATH, "addons")
MEDIA_PATH = os.path.join(APP_PATH, "media")
DB_PATH = os.path.join(APP_PATH, "db")
DB_FILE = os.path.join(DB_PATH, "db.sqlite")
#LOCK_FILE = os.path.join(APP_PATH, "process.lock") #allow single app instance. not implemented.
#Internationalization
LOCALE_PATH = os.path.join(APP_PATH, "Locale")

#plugins
PLUGIN_CONFIG_FILE = "config.ini"

#file constants
FILE_BUFSIZE = 1024 * 1024 #1MB, 0 = no buffer, -1 = OS buffer.

#os constants
OS_WIN = False
OS_UNIX = False
OS_OSX = False
if 'win32' in sys.platform.lower():
    OS_WIN = True
elif 'darwin' in sys.platform.lower():
    OS_OSX = True
else:
    OS_UNIX = True

#logger constants
LOG_NAME = "error.log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
LOG_MODE = "wb"
LOG_FILE = os.path.join(APP_PATH, LOG_NAME)
#OLD_NAME = "error_old.log"
#OLD_LOG = os.path.join(APP_PATH, OLD_NAME)

#Update constants
UPDATE_URL = "http://www.ochdownloader.com/update.txt"
UPDATE_UNIX_URL = "http://www.ochdownloader.com/updateunix.txt"
#UPDATE_PATH = os.path.join(APP_PATH, "update.exe")

#proxy constants
PROXY_SOCKS5 = "socks5"
PROXY_SOCKS4 = "socks4"
PROXY_HTTP = "http"

#status constants
STATUS_RUNNING = "Running"
STATUS_STOPPED = "Stopped"
STATUS_QUEUE = "Queue"
STATUS_FINISHED = "Finished"
STATUS_ERROR = "Error"

#link status constants
LINK_ALIVE = "Alive"
LINK_DEAD = "Dead"
LINK_UNAVAILABLE = "Unavailable"
LINK_ERROR = "Error"
LINK_CHECKING = "Checking"

#account status constants
ACCOUNT_PREMIUM = "Premium"
ACCOUNT_FREE = "Free"
ACCOUNT_FAIL= "Fail" #login fail
ACCOUNT_ERROR = "Error" #cant connect
ACCOUNT_CHECKING = "Checking"

#unavailable names
UNKNOWN = "Unknown"
UNSUPPORTED = "unsupported"

#Download features
DL_RESUME = "can_reconnect"
DL_PREMIUM = "is_premium"


if __name__ == "__main__":
    print sys.argv[0]
    print os.path.abspath(os.path.dirname(sys.argv[0]))
    print APP_PATH
