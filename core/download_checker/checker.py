import threading
import importlib
import logging
logger = logging.getLogger(__name__)

from core import cons
from core import utils


class LinkChecker(threading.Thread):
    """"""
    def __init__(self, link):
        """"""
        threading.Thread.__init__(self)
        self.file_name = cons.UNKNOWN
        self.host = utils.get_host(link)
        self.link = link
        self.size = 0
        self.link_status = cons.LINK_CHECKING
        self.status_msg = None

    def run(self):
        """"""
        self.check()

    def check(self):
        """"""
        try:
            module = importlib.import_module("plugins.{0}.link_checker".format(self.host))
            self.link_status, file_name, self.size, self.status_msg = module.LinkChecker().check(self.link)
            self.file_name = utils.normalize_file_name(file_name)
        except ImportError as err:
            logger.debug(err)
            self.file_name = utils.normalize_file_name(utils.get_filename_from_url(self.link)) or cons.UNKNOWN #may be an empty str
            self.link_status = cons.LINK_ERROR
        except Exception as err:
            logger.exception(err)
            self.link_status = cons.LINK_ERROR