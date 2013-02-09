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
        self.thread_downloads = {} #{id_item: thread_instance, }, active downloads only.
        self.bucket = TokenBucket() #rate-limit bandwidth
    
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
        while threads:
            for th in threads[:]:
                th.stop_flag = True
                if th.is_alive():
                    th.join(0.1)
                else:
                    threads.remove(th)
    
    def get_thread_update(self, id_item):
        """"""
        th = self.thread_downloads[id_item]

        if th.error_flag and th.stop_flag: #fix on stopped failed download
            status = cons.STATUS_STOPPED
        else:
            status = th.status #get before any other attr

        chunks, size_complete = th.get_chunk_n_size()

        return th.file_name, status, th.size_file, size_complete, th.start_time,\
               th.size_tmp, chunks, th.status_msg, th.can_resume, th.is_premium, th.video_quality

    def is_limit_exceeded(self, id_item):
        th = self.thread_downloads[id_item]
        return th.limit_exceeded