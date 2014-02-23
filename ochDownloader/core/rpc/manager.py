import logging

from . import server
from . import client
from .parser import ParseArgs
from core.utils.concurrent.thread import Future

logger = logging.getLogger(__name__)


class RPCManager:

    def __init__(self, args):
        self.args = args
        self.arguments = self.get_parsed_args()
        self.is_server = False
        self.is_client = False

    def get_parsed_args(self):
        parser = ParseArgs(self.args)
        return parser.arguments

    def setup_server(self):
        # TODO: add future daemon
        th = Future(target=server.start)
        #th.daemon = True
        self.is_server = True

    def setup_client(self):
        client.start(self.arguments)
        self.is_client = True

    def start_worker(self):
        if self.arguments.ipc:
            self.setup_client()
        else:
            self.setup_server()