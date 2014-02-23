import logging
from collections import OrderedDict

from core import cons
from core.utils.concurrent.thread import Future

from .worker import worker
from .item import CheckItem, CheckingItem

logger = logging.getLogger(__name__)


class DownloadCheckerManager:

    def __init__(self):
        self.pending_downloads = OrderedDict()  # {uid: item, }
        self.checking_downloads = {}  # {uid: CheckingItem, }
        self.ready_downloads = {}  # {uid: item, }
        self._active_limit = 20

    def clear(self):
        self.pending_downloads.clear()
        self.checking_downloads.clear()
        self.ready_downloads.clear()

    def create_item(self, url):
        item = CheckItem(url)
        item.status = cons.LINK_CHECKING
        item.name = cons.UNKNOWN
        return item

    def add(self, item):
        self.pending_downloads[item.uid] = item
    
    def start_checking(self):
        for uid, item in list(self.pending_downloads.items()):
            if len(self.checking_downloads) >= self._active_limit:
                break

            del self.pending_downloads[uid]
            checking = CheckingItem(item)
            checking.thread = Future(target=worker, args=(item.plugin, item.url))
            self.checking_downloads[uid] = checking

    def update(self):
        result = []

        for uid, checking in list(self.checking_downloads.items()):
            if not checking.thread.done():
                continue

            checking.item.status, checking.item.name,\
                checking.item.size, checking.item.status_msg = checking.thread.result()
            self.ready_downloads[uid] = checking.item
            del self.checking_downloads[uid]
            result.append(checking.item)

        if result:
            self.start_checking()

        return result
    
    def recheck(self):
        for uid, item in list(self.ready_downloads.items()):
            if item.status in (cons.LINK_CHECKING, cons.LINK_ALIVE):
                continue

            item.status = cons.LINK_CHECKING
            self.pending_downloads[uid] = item
            del self.ready_downloads[uid]

        self.start_checking()

    def pop(self, id_item_list):
        """"""
        result = []

        for uid in id_item_list:
            item = self._pop(uid)
            result.append(item)

        if result:
            self.start_checking()
            
        return result

    def _pop(self, uid):
        try:
            checking = self.checking_downloads.pop(uid)
            return checking.item
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