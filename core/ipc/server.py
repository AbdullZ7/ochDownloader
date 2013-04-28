import os
import asyncore
import socket
import logging
logger = logging.getLogger(__name__)

from core import cons

from .parser import ParseArgs


class ServerHandler(asyncore.dispatcher):
    def __init__(self, *args, **kwargs):
        asyncore.dispatcher.__init__(self, *args, **kwargs)
        self.data = []

    def handle_read(self):
        data = self.recv(8192)
        self.data.append(data)

    def handle_close(self):
        args = ''.join(self.data).strip().split(' ')
        ParseArgs(args)
        del self.data[:]
        self.close()


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
    server = Server('localhost', 0)
    write_file(str(server.port_))
    asyncore.loop()  # blocks


def write_file(port):
    try:
        with open(cons.IPC_PORT_FILE, "wb") as fh:
            fh.write(port)
    except EnvironmentError as err:
        logger.exception(err)


if __name__ == "__main__":
    server = Server('localhost', 0)
    # Note that here loop is infinite (count is not given)
    asyncore.loop()  # blocks