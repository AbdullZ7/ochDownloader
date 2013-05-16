import logging
logger = logging.getLogger(__name__)

from core.download.downloader import Downloader
from core.network.token_bucket import TokenBucket #rate limit bandwidth
from core import cons


class ThreadManager:
    """
    Downloads thread manager.
    """
    def __init__(self):
        self.thread_downloads = {} # {id_item: thread_instance, }, active downloads only.
        self.bucket = TokenBucket() # rate-limit bandwidth
    
    def get_thread(self, id_item):
        """"""
        return self.thread_downloads[id_item]

    def create_thread(self, download_item):
        """"""
        th = Downloader(download_item, self.bucket)
        self.thread_downloads[download_item.id] = th
        th.start()

    def delete_thread(self, id_item):
        """"""
        del self.thread_downloads[id_item]

    def stop_thread(self, id_item):
        """"""
        th = self.thread_downloads[id_item]
        th.stop_flag = True
        #th.join()
    
    def stop_all_threads(self):
        """"""
        logger.debug("Asking threads to exit.")
        threads = self.thread_downloads.values()

        for th in threads:
            th.stop_flag = True

        for th in threads:
            th.join()