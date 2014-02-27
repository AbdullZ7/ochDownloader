import os
import logging
from collections import OrderedDict

from core import const
from core import signals
from core import utils
from core.config import conf
from core.plugin.config import services_dict
from core.utils.concurrent.thread import Future
from .http import downloader
from .http.worker import bucket
from .item import ActiveItem

logger = logging.getLogger(__name__)


class DownloadManager:

    def __init__(self):
        self.active_downloads = {}  # {uid: ActiveItem, }
        self.queue_downloads = OrderedDict()
        self.complete_downloads = {}
        self.stopped_downloads = {}
        self._active_limit = 5

    def reorder_queue(self, id_order_list):
        ordered_items_dict = OrderedDict()

        for uid in id_order_list:
            try:
                ordered_items_dict[uid] = self.queue_downloads[uid]
            except KeyError:
                pass

        if len(self.queue_downloads) == len(ordered_items_dict):
            self.queue_downloads.clear()
            self.queue_downloads.update(ordered_items_dict)
        else:
            logger.warning("reorder_queue failed")
    
    def start_all(self, id_order_list):
        self.queue_downloads.update(self.stopped_downloads)
        self.stopped_downloads.clear()
        self.reorder_queue(id_order_list)
        self.next_download()
    
    def stop_all(self):
        for item in self.active_downloads.values():
            item.stop()

        for uid, item in list(self.queue_downloads.items()):
            self.stopped_downloads[uid] = item
            del self.queue_downloads[uid]

    def start(self, uid):
        try:
            item = self.stopped_downloads.pop(uid)
        except KeyError:
            return False

        self.queue_downloads[uid] = item
        self.next_download()
        return True

    def stop(self, uid):
        try:
            item = self.active_downloads[uid]
        except KeyError:
            pass
        else:
            item.stop()
            return True

        try:
            item = self.queue_downloads.pop(uid)
        except KeyError:
            pass
        else:
            self.stopped_downloads[uid] = item
            return True

        return False

    def delete(self, uid, remove_file=False):
        item = self._delete(uid)

        if remove_file:
            if isinstance(item, ActiveItem):
                Future(target=self._remove_file, args=(item, ))
            else:
                utils.remove_file(os.path.join(item.path, item.name))

    def _delete(self, uid):
        try:
            item = self.active_downloads.pop(uid)
        except KeyError:
            pass
        else:
            item.stop()
            self.next_download()
            return item

        try:
            return self.stopped_downloads.pop(uid)
        except KeyError:
            pass

        try:
            return self.queue_downloads.pop(uid)
        except KeyError:
            pass

        try:
            return self.complete_downloads.pop(uid)
        except KeyError:
            raise

    def _remove_file(self, active):
        active.thread.result(wait=True)
        utils.remove_file(os.path.join(active.item.path, active.item.name))

    def update(self):
        result = []

        for uid, active in list(self.active_downloads.items()):
            active.update()

            if not active.thread.done():
                continue

            active.thread.result()

            item = active.item
            old_status = item.status

            if old_status == const.STATUS_STOPPED:
                self.stopped_downloads[uid] = item
            elif old_status == const.STATUS_FINISHED:
                self.complete_downloads[uid] = item
            else:  # status == cons.STATUS_ERROR
                item.fail_count += 1

                if item.fail_count > conf.get_retries_limit():
                    item.status = const.STATUS_STOPPED
                    self.stopped_downloads[uid] = item
                else:
                    item.status = const.STATUS_QUEUE
                    self.queue_downloads[uid] = item

            del self.active_downloads[uid]
            self.next_download()

            if old_status == const.STATUS_FINISHED:
                signals.download_complete.emit(item)

            if not self.active_downloads and not old_status == const.STATUS_STOPPED:
                signals.all_downloads_complete.emit()

            if item.limit_exceeded and self.active_downloads and old_status == const.STATUS_ERROR:
                signals.limit_exceeded.emit()

            result.append(item)

        return result

    def add_to_downloader(self, download_item):
        self.queue_downloads[download_item.uid] = download_item

    def next_download(self):
        for item in list(self.queue_downloads.values()):
            if len(self.active_downloads) >= self._active_limit:
                break

            self.download_starter(item)

    def download_starter(self, item):
        if self.is_host_slot_available(item.host): # and host_accounts.get_account(download_item.host) is None:
            item.fail_count = 0
            active = ActiveItem(item)
            active.thread, active.queue, active.stop_event = downloader.spawn(item)
            self.active_downloads[item.uid] = active
            del self.queue_downloads[item.uid]

    def is_host_slot_available(self, host):
        try:
            service = services_dict[host]
        except KeyError:
            return True

        host_slots = service.get_slots_limit()

        if host_slots <= 0:  # -1 or 0 means unlimited slots
            return True

        count = 0
        for active in self.active_downloads.values():
            if host == active.item.host:
                count += 1

            if count >= host_slots:
                return False

        return True

    def new_slot_limit(self, new_limit):
        current_limit = self._active_limit
        self._active_limit = new_limit

        if new_limit > current_limit:
            self.next_download()

    def new_rate_limit(self, new_limit):
        bucket.rate_limit(new_limit)

    def stop_all_threads(self):
        logger.debug("Asking threads to exit.")

        for active in self.active_downloads.values():
            active.stop()

        for active in self.active_downloads.values():
            active.thread.result(wait=True)