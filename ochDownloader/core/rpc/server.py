import logging
from xmlrpc.server import SimpleXMLRPCServer

from core import signals
from core import utils
from core import const

logger = logging.getLogger(__name__)
port = 8000


def start():
    # TODO: get port from config.ini
    try:
        server = SimpleXMLRPCServer(("localhost", port))
        server.register_introspection_functions()
        server.register_function(add_raw_downloads)
    except Exception as err:
        logger.exception(err)


def add_raw_downloads(links, cookie, path):
    path = path or const.DLFOLDER_PATH

    if cookie is not None:
        cj = utils.load_cookie(cookie)
    else:
        cj = None

    signals.add_raw_downloads.emit(links, path, cj)