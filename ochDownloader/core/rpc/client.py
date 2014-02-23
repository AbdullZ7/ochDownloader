import logging
import xmlrpc.client

logger = logging.getLogger(__name__)
port = 8000


def start(arguments):
    try:
        client = xmlrpc.client.ServerProxy('http://localhost:' + str(port))
        client.add_raw_downloads(arguments.links, arguments.cookie, arguments.path)
    except Exception as err:
        logger.exception(err)