import logging

from core import const
from .download.manager import DownloadManager
from .download.item import DownloadItem
from .check.manager import DownloadCheckerManager
#from .update_manager import UpdateManager
#from .session import SessionParser

logger = logging.getLogger(__name__)


class _Api:
    """"""
    def __init__(self):
        """"""
        self.downloader = DownloadManager()
        self.checker = DownloadCheckerManager()
        #self.accounts = AccountManager()
        #self.session_parser = SessionParser()

    def create_download_item(self, url):
        return DownloadItem(url)
    
    def start_update_manager(self):
        #update_manager = UpdateManager() #new thread.
        #update_manager.start()
        #return update_manager
        pass
    
    def get_active_downloads(self):
        return self.downloader.active_downloads.copy()
    
    def get_queue_downloads(self):
        return self.downloader.queue_downloads.copy()
    
    def get_complete_downloads(self):
        return self.downloader.complete_downloads.copy()
    
    def get_stopped_downloads(self):
        return self.downloader.stopped_downloads.copy()
    
    def get_all_downloads(self):
        all_downloads = {}
        all_downloads.update(self.downloader.active_downloads)
        all_downloads.update(self.downloader.queue_downloads)
        all_downloads.update(self.downloader.stopped_downloads)
        all_downloads.update(self.downloader.complete_downloads)
        return all_downloads

    def clear_complete(self):
        self.downloader.complete_downloads.clear()

    def save_download_as(self, download_item, save_as):
        download_item.save_as = save_as

    def set_download_name(self, download_item, name):
        download_item.name = name
    
    def load_session(self):
        FILE_NAME, FILE_PATH, LINK, HOST, SIZE, PROGRESS, TIME, CHUNKS, QUALITY, SAVE_AS = range(10)
        ordered_list = []
        download_list = self.session_parser.load()
        try:
            for item in download_list:
                download_item = self.create_download_item(item[LINK])
                download_item.path = item[FILE_PATH]
                download_item.name = item[FILE_NAME]
                download_item.status = const.STATUS_STOPPED
                download_item.progress = item[PROGRESS]
                download_item.size = item[SIZE]
                download_item.time = item[TIME]
                download_item.chunks = item[CHUNKS]
                download_item.video_quality = item[QUALITY]
                download_item.save_as = item[SAVE_AS]
                self.downloader.stopped_downloads[download_item.uid] = download_item
                ordered_list.append(download_item)
        except Exception as err:
            logger.exception(err)
            self.downloader.stopped_downloads.clear()
            return []
        return ordered_list
    
    def save_session(self, id_item_list):
        download_list = []
        all_downloads = self.get_all_downloads()
        for download_item in (all_downloads[id_item] for id_item in id_item_list): #generator
            if download_item.status != const.STATUS_FINISHED:
                download_list.append([download_item.name, download_item.path, download_item.url, download_item.host,
                                      download_item.size, download_item.progress, download_item.time, download_item.chunks,
                                      download_item.video_quality, download_item.save_as])
        self.session_parser.save(download_list)
        logger.debug("Session has been saved")

    def get_download_items(self, id_item_list):
        """"""
        all_downloads = self.get_all_downloads()
        return [all_downloads[id_item] for id_item in id_item_list]

    def get_checking_download_item(self, id_item):
        all_checker = {}
        all_checker.update(self.checker.pending_downloads)
        all_checker.update(self.checker.checking_downloads)
        all_checker.update(self.checker.ready_downloads)
        return all_checker[id_item]


api = _Api()