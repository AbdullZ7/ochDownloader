import asyncore
import socket
import logging
logger = logging.getLogger(__name__)

from .server import FILE


class Client(asyncore.dispatcher):
    def __init__(self, host, port, data):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.buffer = data

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        logger.debug(self.recv(8192))

    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]


def start():
    port = get_port_from_file()
    client = Client('localhost', port, data)
    asyncore.loop()  # blocks


def get_port_from_file():
    with open(FILE, "rb") as fh:
        port = int(fh.read().strip())
    return port


if __name__ == "__main__":
    data = "some"
    client = Client('localhost', get_port_from_file(), data)
    # Note that here loop is infinite (count is not given)
    asyncore.loop() #blocks