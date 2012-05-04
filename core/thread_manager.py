import threading
import time
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from network.downloader import Downloader
from network.token_bucket import TokenBucket #rate limit bandwidth
import cons

RETRIES = 5
RETRY_TIME = 60


class ThreadManager:
    """
    Downloads thread manager.
    """
    def __init__(self):
        self.thread_downloads = {} #{id_item: thread_instance, }, solo descargas activas.
        self.bucket = TokenBucket() #rate-limit bandwidth
    
    def get_thread(self, id_item):
        """"""
        try:
            return self.thread_downloads[id_item]
        except KeyError as err:
            logger.exception(err)
            return None
    
    def add_thread(self, id_item, file_name, save_to_path, link, host, chunks): #get_source es un metodo de plugin_bridge.
        """
        """
        th = Downloader(file_name, save_to_path, link, host, self.bucket, chunks) #atributos: file_name, path_fsaved, size_file, size_saved, progress, etc
        self.thread_downloads[id_item] = th #crear un nuevo item (clave: valor) en el dict thread, con nombre de archivo (clave) e instancia correspondiente (valor)
        th.start()
        
    def delete_thread(self, id_item):
        """"""
        if id_item in self.thread_downloads:
            del self.thread_downloads[id_item] #remover el item del diccionario.
        
    def stop_thread(self, th):
        """"""
        if th is not None:
            th.stop_flag = True
            #th.join()
    
    def stop_all_threads(self): #Usar antes de salir del programa.
        """"""
        logger.debug("Asking threads to exit.")
        threads = self.thread_downloads.values()
        while threads:
            for th in threads[:]:
                th.stop_flag = True #detener descarga
                if th.is_alive():
                    th.join(0.1)
                else:
                    threads.remove(th)
    
    def get_thread_status(self, id_item):
        """"""
        th = self.get_thread(id_item)
        
        if th is not None:
            status = th.status
            if status in (cons.STATUS_FINISHED, cons.STATUS_STOPPED, cons.STATUS_ERROR):
                speed = 0
                progress = 100 if status == cons.STATUS_FINISHED else th.get_progress()
                if th.stop_flag and th.status == cons.STATUS_ERROR: #fix on stopped failed download
                    status = cons.STATUS_STOPPED
            else:
                speed = th.get_speed()
                progress = th.get_progress()
            status_msg = th.status_msg
            
            chunks, size_complete = th.get_chunk_n_size()
            
            return (th.file_name, status, progress, th.size_file, size_complete, speed, th.get_time(), th.get_remain(), chunks, status_msg, th.can_resume, th.is_premium) #metodos del Downloader.
            #NAME, STATUS, PROGRESS, SIZE, COMPLETE, SPEED, TIME, REMAIN, CHUNKS, MSG, RESUME, PREMIUM = range(12)
        
        return None

    def is_limit_exceeded(self, id_item):
        """"""
        th = self.get_thread(id_item)
        
        if th is not None:
            return th.limit_exceeded
        else:
            return False
