import threading
#import Queue

from .decrypt import Decrypter


class DecryptManager:
    def __init__(self):
        self.th = None
        self.pending_downloads = []
        self.running = False
        #self.queue = Queue.Queue(1) # progress

    def add(self, download_item):
        self.pending_downloads.append(download_item)
        self.next()

    def next(self):
        if not self.running:
            if self.pending_downloads:
                download_item = self.pending_downloads.pop(0)
                self.th = Decrypter(download_item)
                self.th.start()
                self.running = True

    def get_update(self):
        if self.th is not None:
            if not self.th.is_alive():
                self.running = False
            return self.th.id_item, self.th.status, self.th.is_alive()
        else:
            return