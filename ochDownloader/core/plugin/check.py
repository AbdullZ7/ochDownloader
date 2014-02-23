import re
import logging
from http import cookiejar
from contextlib import closing

from .exceptions import StopParsing, ParsingError
from core import utils
from core import cons
from core.utils.http import request

logger = logging.getLogger(__name__)

BUFF_SZ = 1024 * 1024  # 1MB


class PluginCheckBase:
    """"""
    def __init__(self, url):
        """"""
        self.url = url
        self.status = cons.LINK_ERROR
        self.name = None
        self.size = 0
        self.message = None

    def parse(self):
        raise NotImplementedError()