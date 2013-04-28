import threading
import logging
logger = logging.getLogger(__name__)

import server
from .client import ClientManager, SocketError, FilePortError
from .parser import ParseArgs


class IPCManager:
    def __init__(self, args):
        self.args = args
        self.arguments = self.get_parsed_args()
        self.is_server = False
        self.is_client = False

    def get_parsed_args(self):
        args_parser = ParseArgs(self.args)
        return args_parser.arguments

    def send(self):
        # do if self.arguments.ipc is True
        data = " ".join(self.args)
        self.setup_client(data)

    def setup_server(self):
        th = threading.Thread(group=None, target=server.start, name=None)
        th.daemon = True
        th.start()
        self.is_server = True

    def setup_client(self, data):
        client = ClientManager(data)
        th = threading.Thread(group=None, target=client.start, name=None)
        th.daemon = True
        th.start()
        self.is_client = True

    def start_worker(self):
        if self.arguments.ipc:
            try:
                self.send()
            except (SocketError, FilePortError):
                self.setup_server()
                #events.add_downloads.emit(...
        else:
            self.setup_server()