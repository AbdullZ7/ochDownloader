import os
import asyncore
import socket
import logging
logger = logging.getLogger(__name__)

from core import cons
from core import utils
from core import events

from .parser import ParseArgs


class ServerHandler(asyncore.dispatcher):
    def __init__(self, *args, **kwargs):
        asyncore.dispatcher.__init__(self, *args, **kwargs)
        self.data = []

    def handle_read(self):
        data = self.recv(8192)
        self.data.append(data)

    def handle_close(self):
        self.close()
        self.emit()

    def emit(self):
        args = ''.join(self.data).strip().split(' ')
        parser = ParseArgs(args)
        if parser.arguments.links is not None:
            path = parser.arguments.path or cons.DLFOLDER_PATH
            links = parser.arguments.links
            if parser.arguments.cookie is not None:
                cj = utils.load_cookie(parser.arguments.cookie)
            else:
                cj = None
            events.add_downloads.emit(links, path, cj)
        #del self.data[:]


class Server(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.port_ = self.getsockname()[1]
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            handler = ServerHandler(sock)

    def handle_close(self):
        self.close()


def start():
    try:
        server = Server('localhost', 0)
        write_file(str(server.port_))
        asyncore.loop()  # blocks
    except Exception as err:
        logger.exception(err)


def write_file(port):
    try:
        with open(cons.IPC_PORT_FILE, "wb") as fh:
            fh.write(port)
    except EnvironmentError as err:
        logger.exception(err)