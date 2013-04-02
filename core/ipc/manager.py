import threading
import logging
logger = logging.getLogger(__name__)

import server
import client
from .parser import ParseArgs


class IPCManager:
    def __init__(self, args):
        self.args = args
        self.arguments = self.get_parsed_args()

    def get_parsed_args(self):
        args_parser = ParseArgs(self.args)
        return args_parser.arguments

    def send(self):
        # do if self.arguments.ipc is True
        data = " ".join(self.args)
        self.setup_client(data)

    def setup_server(self):
        threading.Thread(group=None, target=server.start, name=None)

    def setup_client(self, data):
        threading.Thread(group=None, target=client.start, name=None, args=(data, ))