#! /usr/bin/python3

import sys


requires = (3, 3)

if (sys.version_info[0], sys.version_info[1]) != requires:
    sys.exit("Python %s.%s is required. Yours is %s" % (requires[0], requires[1], sys.version))


import logging
import logging.handlers
import os

from core import const

logger = logging.getLogger(__name__)


def except_hook(exc_type, exc_value, exc_tb):
    if isinstance(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

sys.excepthook = except_hook


def create_config_folder():
    if not os.path.exists(const.HOME_APP_PATH):
        os.makedirs(const.HOME_APP_PATH, exist_ok=True)


def logger_setup():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)-7s %(name)s: %(message)s")
    rotate_mb = 1
    rotating = logging.handlers.RotatingFileHandler(const.LOG_FILE,
                                                    mode="a",
                                                    encoding='utf-8',
                                                    maxBytes=rotate_mb * 1024 * 1024,
                                                    backupCount=5)
    rotating.setLevel(logging.INFO)
    rotating.setFormatter(logging.Formatter(const.LOG_FORMAT))
    logging.getLogger().addHandler(rotating)


def gettext_setup():
    import locale
    import gettext

    lc, encoding = locale.getdefaultlocale()
    lc_sub_lang = lc.lower().replace("_", "-")  # ie: es-ar
    lc_lang = lc.split("_")[0]  # ie: es
    lang = gettext.translation(const.APP_NAME, const.LOCALE_PATH,
                               languages=[lc_sub_lang, lc_lang, ],
                               fallback=True)
    lang.install()  # install _() on builtins namespace


def start_app():
    #from core.ipc.manager import IPCManager

    #ipc_manager = IPCManager(sys.argv[1:])
    #ipc_manager.start_worker()

    #if ipc_manager.is_server:
    logger.info("Start GUI")
    #start_gui()


#def start_gui():
    #from PySide.QtGui import QApplication
    #from ui.qt.main import Gui

    #app = QApplication([''])  # QApplication(sys.argv)
    #gui = Gui()
    #app.exec_()  # Exceptions in the main loop are all caught by pySide!


#def clean_up():
    #from core.api import api
    #from core.dispatch import idle

    #idle.set_events()  # quit pending events.
    #api.downloader.stop_all_threads()


if __name__ == "__main__":
    create_config_folder()
    logger_setup()
    gettext_setup()
    #start_app()
    #clean_up()
    sys.exit()