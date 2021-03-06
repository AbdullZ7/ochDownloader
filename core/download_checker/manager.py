import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

from core import cons
from core.slots import Slots
from checker import LinkChecker


class DownloadCheckerManager:
    """"""
    def __init__(self):
        """"""
        self.__slots = Slots(limit=20) #checker stots
        self.__pending_downloads = OrderedDict() #{id_item: download_item, }
        self.__checking_downloads = {} #{id_item: download_item, }
        self.__ready_downloads = {} #{id_item: download_item, } checked_downloads
        self.__thread_checking_downloads = {} #{id_item: th, }

    def get_checking_downloads(self):
        return self.__checking_downloads.copy()

    def get_all_checking_downloads(self):
        all_downloads = {}
        all_downloads.update(self.__pending_downloads)
        all_downloads.update(self.__checking_downloads)
        all_downloads.update(self.__ready_downloads)
        return all_downloads

    def clear_pending(self):
        """
        Erase pending_downloads dicts
        """
        self.__pending_downloads.clear()
        self.__checking_downloads.clear()
        self.__ready_downloads.clear()
        self.__thread_checking_downloads.clear()
        self.__slots.slots = 0

    def add_to_checker(self, download_item):
        self.__pending_downloads[download_item.id] = download_item
    
    def start_checking(self):
        """"""
        for id_item, download_item in self.__pending_downloads.items():
            if self.__slots.add_slot():
                th = LinkChecker(download_item)
                th.start()
                self.__thread_checking_downloads[id_item] = th
                self.__checking_downloads[id_item] = download_item
                del self.__pending_downloads[id_item]
            else:
                break

    def update_checking_downloads(self):
        """
        This may change the checking_downloads dict, you should get a dict copy before calling this method.
        """
        for id_item, download_item in self.__checking_downloads.items():
            th = self.__thread_checking_downloads[id_item]
            if not th.is_alive():
                download_item.link_status = th.link_status
                download_item.size = th.size
                download_item.status_msg = th.status_msg
                if download_item.name == cons.UNKNOWN: #may be downloading
                    download_item.name = th.file_name
                self.__ready_downloads[id_item] = download_item
                del self.__checking_downloads[id_item]
                del self.__thread_checking_downloads[id_item]
                self.__slots.remove_slot()
                self.start_checking()
    
    def recheck_items(self):
        """"""
        for id_item, download_item in self.__ready_downloads.items():
            if download_item.link_status not in (cons.LINK_CHECKING, cons.LINK_ALIVE):
                download_item.link_status = cons.LINK_CHECKING #safe
                self.__pending_downloads[id_item] = download_item
                del self.__ready_downloads[id_item]
        self.start_checking()

    def pop_checking_items(self, id_item_list):
        """"""
        result_list = []
        for id_item in id_item_list: # add this items.
            try:
                download_item = self.__checking_downloads.pop(id_item)
            except KeyError:
                try:
                    download_item = self.__ready_downloads.pop(id_item)
                except KeyError:
                    try:
                        download_item = self.__pending_downloads.pop(id_item)
                    except KeyError:
                        raise
            else:
                del self.__thread_checking_downloads[id_item]
                self.__slots.remove_slot()
                #self.start_checking()

            result_list.append(download_item)

        self.start_checking()
            
        return result_list