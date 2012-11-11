import asyncore
import socket


class ServerHandler(asyncore.dispatcher):
    def __init__(self, *args, **kwargs):
        asyncore.dispatcher.__init__(self, *args, **kwargs)
        self.data = []

    def handle_read(self):
        data = self.recv(8192)
        self.data.append(data)

    def handle_close(self):
        print ''.join(self.data)
        print "close serverhandler"
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
            print 'Incoming connection from %s' % repr(addr)
            handler = ServerHandler(sock)

    def handle_close(self):
        self.close()

def start():
    server = Server('localhost', 0)
    asyncore.loop() #blocks


if __name__ == "__main__":
    server = Server('localhost', 0)
    # Note that here loop is infinite (count is not given)
    asyncore.loop() #blocks