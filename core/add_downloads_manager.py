import threading
import importlib
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

import cons
import misc
from download_core import DownloadItem
from slots import Slots


class LinkChecker(threading.Thread):
    """"""
    def __init__(self, link):
        """"""
        threading.Thread.__init__(self)
        self.file_name = cons.UNKNOWN
        self.host = misc.get_host(link)
        self.link = link
        self.size = 0
        self.link_status = cons.LINK_CHECKING
        self.status_msg = None

    def run(self):
        """"""
        self.check()

    def check(self):
        """"""
        try:
            module = importlib.import_module("plugins.{0}.link_checker".format(self.host))
        except ImportError as err:
            logger.debug(err)
            self.file_name = misc.get_filename_from_url(self.link) or cons.UNKNOWN #may be an empty str
            self.link_status = cons.LINK_ERROR
            self.host = cons.UNSUPPORTED
        except Exception as err:
            logger.exception(err)
            self.link_status = cons.LINK_ERROR
            self.host = cons.UNSUPPORTED
        else:
            self.link_status, file_name, self.size, self.status_msg = module.LinkChecker().check(self.link)
            self.file_name = misc.smart_decode(misc.html_entities_parser(file_name))


class AddDownloadsManager:
    """"""
    def __init__(self):
        """"""
        self.__slots = Slots(limit=20) #checker stots
        self.__pending_downloads = OrderedDict() #{id_item: download_item, }
        self.__checking_downloads = {} #{id_item: download_item, }
        self.__ready_downloads = {} #{id_item: download_item, } checked_downloads
        self.__thread_checking_downloads = {} #{id_item: th, }

    def clear_pending(self):
        """
        Erase pending_downloads dicts
        """
        self.__pending_downloads.clear()
        self.__checking_downloads.clear()
        self.__ready_downloads.clear()
        self.__thread_checking_downloads.clear()
        self.__slots.set_slots(slots=0)

    def create_download_item(self, file_name, size, link, copy_link=True):
        """"""
        host = misc.get_host(link)
        download_item = DownloadItem(file_name, host, size, link, can_copy_link=copy_link)
        self.__pending_downloads[download_item.id] = download_item
        return download_item
    
    def start_checking(self):
        """"""
        for id_item, download_item in self.__pending_downloads.items():
            if self.__slots.add_slot():
                th = LinkChecker(download_item.link)
                th.start()
                self.__thread_checking_downloads[id_item] = th
                self.__checking_downloads[id_item] = download_item
                del self.__pending_downloads[id_item]
            else:
                break

    def get_checking_update(self):
        """"""
        result_list = []
        for id_item, download_item in self.__checking_downloads.items():
            result_list.append(download_item)
            th = self.__thread_checking_downloads[id_item]
            if not th.is_alive():
                download_item.host = th.host
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
        return result_list
    
    def recheck_items(self):
        """"""
        for id_item, download_item in self.__ready_downloads.items():
            if download_item.link_status not in (cons.LINK_CHECKING, cons.LINK_ALIVE):
                download_item.link_status = cons.LINK_CHECKING #safe
                self.__pending_downloads[id_item] = download_item
                del self.__ready_downloads[id_item]
                self.start_checking()

    def get_added_items(self, id_add_list): #get download_items (added) from pending.
        """"""
        result_list = []
        for id_item in id_add_list: #add this items.
            try:
                download_item = self.__checking_downloads.pop(id_item)
                del self.__thread_checking_downloads[id_item]
                self.__slots.remove_slot()
            except:
                try:
                    download_item = self.__ready_downloads.pop(id_item)
                except:
                    try:
                        download_item = self.__pending_downloads.pop(id_item) #so we only keep the non-added items in the pending_dict
                    except Exception as err:
                        download_item = None
                        logger.warning(err)
                
            if download_item is not None:
                result_list.append(download_item)
            
        return result_list