import threading
import importlib
import logging
logger = logging.getLogger(__name__)

from core import cons


class AccountChecker(threading.Thread):
    """"""
    def __init__(self, host, username, password):
        """"""
        threading.Thread.__init__(self)
        self.host = host
        self.username = username
        self.password = password
        self.status = None

    def run(self):
        """"""
        self.check()

    def check(self):
        """"""
        try:
            module = importlib.import_module("plugins.{0}.account".format(self.host))
            account = module.PluginAccount(self.username, self.password)
            account.parse()
        except ImportError as err:
            logger.debug(err)
            self.status = cons.ACCOUNT_FAIL
        except Exception as err:
            logger.exception(err)
            self.status = cons.ACCOUNT_ERROR
        else:
            self.status = account.account_status