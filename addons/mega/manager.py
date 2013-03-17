import os
import multiprocessing
import logging
logger = logging.getLogger(__name__)

from .decrypt import Decrypter


class DecryptManager:
    def __init__(self):
        self.pending_downloads = []
        self.pipe_out, self.pipe_in = multiprocessing.Pipe()

    @property
    def is_running(self):
        if not hasattr(self, 'th'):
            return False
        elif not self.th.is_alive():
            return False
        else:
            return True

    def remove_file(self, path, name):
        try:
            os.remove(os.path.join(path, name))
        except Exception as err:
            logger.warning(err)

    def add(self, download_item):
        self.pending_downloads.append(download_item)
        self.next()

    def next(self):
        if not self.is_running:
            if self.pending_downloads:
                download_item = self.pending_downloads.pop(0)
                self.th = Decrypter(download_item, self.pipe_in)
                self.th.start()
                self.running = True

    def get_update(self):
        if not self.is_running and hasattr(self, 'th'):
            id_item = self.th.id_item
            if self.pipe_out.poll():
                err, status = self.pipe_out.recv()
                if err:
                    logger.error(status)
                else:
                    self.remove_file(self.th.path, self.th.name)
            else:
                status = "Error: Empty pipe"
                logger.error(status)
            self.next()
            return id_item, status
        else:
            return