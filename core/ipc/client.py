import socket
import logging
logger = logging.getLogger(__name__)

from core import cons


class SocketError(Exception): pass
class FilePortError(Exception): pass


class Client:
    def __init__(self, host, port, data):
        self.buffer = data
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def create_socket(self, family, stype):
        self.family_and_type = family, stype
        self.socket = socket.socket(family, stype)

    def connect(self, address):
        try:
            self.socket.connect(address)
        except socket.error as err:
            raise SocketError(err)

    def send(self):
        while self.buffer:
            sent = self.socket.send(self.buffer)
            self.buffer = self.buffer[sent:]
        self.close()

    def close(self):
        self.socket.close()


class ClientManager():
    def __init__(self, data):
        self.port = self.get_port_from_file()
        self.client = Client('localhost', self.port, data)

    def start(self):
        try:
            self.client.send()
        except Exception as err:
            logger.exception(err)

    def get_port_from_file(self):
        try:
            with open(cons.IPC_PORT_FILE, "rb") as fh:
                port = int(fh.read().strip())
        except (EnvironmentError, ValueError) as err:
            logger.exception(err)
            raise FilePortError(err)
        else:
            return port