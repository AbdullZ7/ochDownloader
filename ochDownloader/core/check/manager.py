import logging
from collections import OrderedDict

from core import const
from core.utils.concurrent.thread import Future

from .worker import worker
from .item import CheckItem, CheckWorkerItem

logger = logging.getLogger(__name__)


class DownloadCheckerManager:

    def __init__(self):
        self.pending_downloads = OrderedDict()  # {uid: item, }
        self.checking_downloads = {}  # {uid: CheckWorkerItem, }
        self.ready_downloads = {}  # {uid: item, }
        self._active_limit = 20

    def clear(self):
        self.pending_downloads.clear()
        self.checking_downloads.clear()
        self.ready_downloads.clear()

    def create_item(self, url):
        item = CheckItem(url)
        item.status = const.LINK_CHECKING
        item.name = const.UNKNOWN
        return item

    def add(self, item):
        self.pending_downloads[item.uid] = item
    
    def start_checking(self):
        for uid, item in list(self.pending_downloads.items()):
            if len(self.checking_downloads) >= self._active_limit:
                break

            del self.pending_downloads[uid]
            w_item = CheckWorkerItem(item)
            w_item.thread = Future(target=worker, args=(item.plugin, item.url))
            self.checking_downloads[uid] = w_item

    def update(self):
        result = []

        for uid, w_item in list(self.checking_downloads.items()):
            if not w_item.thread.done():
                continue

            w_item.item.status, w_item.item.name,\
                w_item.item.size, w_item.item.status_msg = w_item.thread.result()
            self.ready_downloads[uid] = w_item.item
            del self.checking_downloads[uid]
            result.append(w_item.item)

        if result:
            self.start_checking()

        return result
    
    def recheck(self):
        for uid, item in list(self.ready_downloads.items()):
            if item.status == const.LINK_ALIVE:
                continue

            item.status = const.LINK_CHECKING
            self.pending_downloads[uid] = item
            del self.ready_downloads[uid]

        self.start_checking()

    def pop(self, id_item_list):
        result = []

        for uid in id_item_list:
            item = self._pop(uid)
            result.append(item)

        if result:
            self.start_checking()
            
        return result

    def _pop(self, uid):
        try:
            w_item = self.checking_downloads.pop(uid)
            return w_item.item
        except KeyError:
            pass

        try:
            return self.ready_downloads.pop(uid)
        except KeyError:
            pass

        try:
            return self.pending_downloads.pop(uid)
        except KeyError:
            raise