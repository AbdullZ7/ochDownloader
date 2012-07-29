import urllib2
import httplib #para excepciones. httplib.HTTPException
import socket
import time #usado en get_speed
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from connection import URLOpen, URLClose

from downloader_core import DownloaderCore


NT_BUFSIZ = 8 * 1024 #8K
DATA_BUFSIZ = 64 * 1024


class SingleDownload(DownloaderCore):
    """"""
    def __init__(self, file_name, path_fsaved, link, host, bucket): #bucket = instancia de algoritmo para limitar la banda. get_source = metodo de plugin_bridge
        """"""
        DownloaderCore.__init__(self, file_name, path_fsaved, link, host, bucket)
        #super().__init__()

    def single_download(self, fh):
        """
        Excepciones manejadas/delegadas a main_download
        """
        buffer_list = []
        len_buffer_data = 0
        def flush_buffer():
            fh.write(''.join(buffer_list))
            del buffer_list[:]
        
        try:
            with URLClose(self.source) as source:
                while True:
                    data = source.read(NT_BUFSIZ)
                    len_data = len(data)
                    
                    buffer_list.append(data)
                    len_buffer_data += len_data
                    self.size_complete += len_data
                    
                    if len_buffer_data >= DATA_BUFSIZ:
                        flush_buffer()
                        len_buffer_data = 0
                    
                    if self.bucket.fill_rate: #self.bucket.fill_rate != 0
                        time.sleep(self.bucket.consume(len_data))
                    
                    if self.stop_flag: #si se detiene (stopped = True).
                        return
                    elif not len_data: #len(data) == 0
                        break
                    
                if self.size_complete < self.size_file: #verification. This should be a not recoverable error if range header is absent (cant resume).
                    raise EnvironmentError("Incomplete Download?")
        except (EnvironmentError, httplib.HTTPException, socket.error) as err: #EnvironmentError incluye urllib2.URLError
            logger.exception(err)
            self.error_flag = True
            self.status_msg = "Error: {0}".format(err)
        finally: #safe
            flush_buffer()


if __name__ == "__main__":
    range = "bytes 11111-222222/33333333"
    
    
    
    
    
