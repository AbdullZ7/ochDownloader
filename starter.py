import warnings #pygtk warnings are redirected to this module.
import logging
import logging.handlers
import os
import sys
import threading

#Libs
import core.cons as cons


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
        self.start_logger()
        self.logger = logging.getLogger(self.__class__.__name__) #self.__class__.__name__ = nombre de la clase
    
    def start_app(self):
        """"""
        self.start_gui()

    def redirect_warnings(self, message, category, filename, lineno, file=None, line=None):
        """"""
        self.logger.warning(warnings.formatwarning(message, category, filename, lineno))

    def start_logger(self):
        """"""
        #config logger
        logging.basicConfig(level=logging.DEBUG,
                            format="%(levelname)-7s %(name)s: %(message)s")

        rotate_mb = 1 #1mb = 1*1024*1024
        rotating = logging.handlers.RotatingFileHandler(cons.LOG_FILE, mode="ab", maxBytes=rotate_mb*1024*1024, backupCount=5)
        rotating.setLevel(logging.INFO)
        rotating.setFormatter(logging.Formatter(cons.LOG_FORMAT))
        logging.getLogger("").addHandler(rotating)

        #rotating.doRollover() #write on a new log file, rotate the previous one.
        
        #doRotate()

    def start_gui(self):
        """"""
        #Gui, create logger first
        from PySide.QtGui import QApplication
        from qt.main import Gui, excepthook, halt, init_gettext
        
        sys.excepthook = excepthook #capturar exceptiones unhandled.
        warnings.showwarning = self.redirect_warnings #capturar pygtk warnings.
        init_gettext() #internacionalization
        try:
            self.logger.info("New app gui instance")
            app = QApplication(['']) #QApplication(sys.argv)
            gui = Gui()
            app.exec_()
        except Exception as err:
            self.logger.exception(err)
            halt() #close gui.

    def clean_up(self):
        from core.api import api
        from core.idle_queue import set_events
        set_events() #quit pending events.
        api.stop_all_threads()

    def exit(self, arg=0):
        self.logger.debug("Exit: {0}".format(arg))
        sys.exit(0)


if __name__ == "__main__":
    #sign_in = SingleAppInstance()
    starter = Starter()
    try:
        installThreadExcepthook() #This allows to log exceptions in threads.
        starter.start_app()
        starter.clean_up()
    except KeyboardInterrupt:
        starter.exit("KeyboardInterrupt.")
    except Exception as err:
        starter.logger.exception(err) #Unhandled error.
        starter.exit("Unhandled Exception!!")
    else:
        starter.exit()
