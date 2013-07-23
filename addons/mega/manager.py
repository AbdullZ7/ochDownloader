import os
import multiprocessing
import logging
logger = logging.getLogger(__name__)

try:
    from addons.unrar.signals import unrar_file
except ImportError:
    unrar_file = None

from core.download.item import DownloadItem

from .decrypt import Decrypter

FILE_EXT = ".crypted"


class Item:
    def __init__(self, id_item, name, path, link):
        self.id_item = id_item
        self.name = name
        self.path = path
        self.link = link
        self.th = None
        self.status = None
        self.out_name = self.get_out_name(name)

    def get_out_name(self, name):
        if name.endswith(FILE_EXT):
            return name[:-len(FILE_EXT)]
        else:
            return name + ".decrypted"


class DecryptManager:
    def __init__(self):
        self.queue_items = []
        self.active_items = []
        self.pipe_out, self.pipe_in = multiprocessing.Pipe()

    def remove_file(self, path, name):
        try:
            os.remove(os.path.join(path, name))
        except Exception as err:
            logger.warning(err)

    def get_active_items(self):
        return self.active_items[:]

    def add(self, download_item):
        item = Item(download_item.id, download_item.name, download_item.path, download_item.link)
        self.queue_items.append(item)
        self.next()

    def next(self):
        if not self.active_items:
            if self.queue_items:
                item = self.queue_items.pop(0)
                item.th = Decrypter(item, self.pipe_in)
                item.th.start()
                item.status = _("Running")
                self.active_items.append(item)

    def update(self):
        # get a copy of active_items before calling this
        for item in self.active_items[:]:
            if not item.th.is_alive():

                if self.pipe_out.poll():
                    err, status = self.pipe_out.recv()
                    if err:
                        logger.error(status)
                    else:
                        self.remove_file(item.path, item.name)
                        if unrar_file is not None:
                            unrar_file.emit(DownloadItem(item.out_name, item.link, path=item.path))
                else:
                    status = "Error: Empty pipe"
                    logger.error(status)

                item.status = status
                self.active_items.remove(item)
                self.next()