import warnings
import logging
import logging.handlers
import sys
import os
import threading

#Libs
from core import cons


def python_version_check():
    ver = sys.version_info
    if not (ver[0], ver[1]) == (2, 7):
        sys.exit("%s needs Python 2.7 to run. Yours is %s" % (cons.APP_NAME, sys.version))


def installThreadExcepthook():
    """
    Workaround for sys.excepthook thread bug
    """
    init_old = threading.Thread.__init__
    def init(self, *args, **kwargs):
        init_old(self, *args, **kwargs)
        run_old = self.run
        def run_with_except_hook(*args, **kw):
            try:
                run_old(*args, **kw)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())
        self.run = run_with_except_hook
    threading.Thread.__init__ = init


class Starter:
    """"""
    def __init__(self):
        """"""
        self.create_config_folder()
        self.setup_logger()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start_app(self):
        """"""
        self.start_gui()

    def redirect_warnings(self, message, category, filename, lineno, file=None, line=None):
        """"""
        self.logger.warning(warnings.formatwarning(message, category, filename, lineno))

    def create_config_folder(self):
        if not os.path.exists(cons.HOME_APP_PATH):
            os.makedirs(cons.HOME_APP_PATH)

    def setup_logger(self):
        """"""
        #config logger
        logging.basicConfig(level=logging.DEBUG,
                            format="%(levelname)-7s %(name)s: %(message)s")

        rotate_mb = 1
        rotating = logging.handlers.RotatingFileHandler(cons.LOG_FILE, mode="ab", maxBytes=rotate_mb*1024*1024, backupCount=5)
        rotating.setLevel(logging.INFO)
        rotating.setFormatter(logging.Formatter(cons.LOG_FORMAT))
        logging.getLogger("").addHandler(rotating)

    def start_gui(self):
        """"""
        from PySide.QtGui import QApplication
        from qt.main import Gui, excepthook, halt, init_gettext

        sys.excepthook = excepthook  # capture unhandled exceptiones.
        warnings.showwarning = self.redirect_warnings  # capture pygtk warnings.
        init_gettext()  # internacionalization

        try:
            self.logger.info("New app gui instance")
            app = QApplication(['']) #QApplication(sys.argv)
            gui = Gui()
            app.exec_()
        except Exception as err:
            self.logger.exception(err)
            halt()  # close gui.

    def clean_up(self):
        from core.api import api
        from core.dispatch.idle_queue import set_events

        set_events()  # quit pending events.
        api.stop_all_threads()

    def exit(self, value=0):
        self.logger.debug("Exit: {0}".format(value))
        sys.exit(value)


if __name__ == "__main__":
    python_version_check()
    starter = Starter()
    try:
        installThreadExcepthook()  # This allows to log exceptions in threads.
        starter.start_app()
        starter.clean_up()
    except KeyboardInterrupt:
        starter.exit("KeyboardInterrupt.")
    except Exception as err:
        starter.logger.exception(err)  # Unhandled error.
        starter.exit("Unhandled Exception!!")
    else:
        starter.exit()
