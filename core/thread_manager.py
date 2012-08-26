import logging
logger = logging.getLogger(__name__)

from network.downloader import Downloader
from network.token_bucket import TokenBucket #rate limit bandwidth
import cons


class ThreadManager:
    """
    Downloads thread manager.
    """
    def __init__(self):
        self.thread_downloads = {} #{id_item: thread_instance, }, active downloads only.
        self.bucket = TokenBucket() #rate-limit bandwidth
    
    def get_thread(self, id_item):
        """"""
        try:
            return self.thread_downloads[id_item]
        except KeyError as err:
            logger.exception(err)
            return None
    
    def add_thread(self, id_item, file_name, save_to_path, link, host, chunks):
        """"""
        th = Downloader(file_name, save_to_path, link, host, self.bucket, chunks)
        self.thread_downloads[id_item] = th
        th.start()

    def delete_thread(self, id_item):
        """"""
        try:
            del self.thread_downloads[id_item]
        except KeyError:
            pass

    def stop_thread(self, th):
        """"""
        if th is not None:
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
    
    def get_thread_status(self, id_item):
        """"""
        th = self.get_thread(id_item)
        
        if th is not None:
            if th.error_flag and th.stop_flag: #fix on stopped failed download
                status = cons.STATUS_STOPPED
            else:
                status = th.status #get before any other attr

            chunks, size_complete = th.get_chunk_n_size()
            
            return th.file_name, status, th.get_progress(), th.size_file, size_complete, th.get_speed(), th.get_time(), th.get_remain(), chunks, th.status_msg, th.can_resume, th.is_premium #metodos del Downloader.
            #NAME, STATUS, PROGRESS, SIZE, COMPLETE, SPEED, TIME, REMAIN, CHUNKS, MSG, RESUME, PREMIUM = range(12)
        
        return None

    def is_limit_exceeded(self, id_item):
        """"""
        th = self.get_thread(id_item)
        
        if th is not None:
            return th.limit_exceeded
        else:
            return False
