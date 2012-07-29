import os
import sys
import urllib
import threading
import time
import logging
logger = logging.getLogger(__name__)

#Local Libs
import core.cons as cons
import core.misc as misc #html entities and numerics parser, etc
from core.plugins_bridge import PluginBridge

from multi_download import MultiDownload


class StatusError(Exception): pass
class StatusStopped(Exception): pass


class Downloader(threading.Thread, MultiDownload):
    """"""
    def __init__(self, file_name, path_fsaved, link, host, bucket, chunks):
        """"""
        threading.Thread.__init__(self) #iniciar threading.Thread
        MultiDownload.__init__(self, file_name, path_fsaved, link, host, bucket, chunks)

    def run(self):
        """"""
        try:
            self.__file_existence_check()
            self.__source()
            self.__validate_source()
            self.__download()
        except (StatusError, StatusStopped) as err:
            if isinstance(err, StatusError):
                self.error_flag = True
                self.status = cons.STATUS_ERROR
                logger.warning(err)
            else:
                self.stop_flag = True
                self.status = cons.STATUS_STOPPED
                logger.info(err)
            self.status_msg = str(err)
        finally:
            if self.source:
                self.source.close()
    
    def __file_existence_check(self):
        """"""
        try:
            if not os.path.exists(self.path_fsaved):
                os.makedirs(self.path_fsaved)
            elif os.path.isfile(self.path_file):
                self.file_exists = True
                start_chunks = [chunks_tuple[0] for chunks_tuple in self.chunks
                                if chunks_tuple[0] < chunks_tuple[1]]
                if start_chunks:
                    self.content_range = min(start_chunks)
        except (EnvironmentError, ValueError) as err:
            logger.exception(err)
            raise StatusError(err)
    
    def __source(self):
        """"""
        pb = PluginBridge(self.link, self.host, self.content_range, self.wait_func)
        pb.plugin_download()
        self.source = pb.source
        if self.stop_flag:
            raise StatusStopped("Stopped")
        elif self.source:
            self.link_file = pb.dl_link
            self.cookie = pb.cookie
            info = self.source.info()
            #print info.headers
            old_file_name = self.file_name
            self.file_name = self.__get_filename_from_source(info)
            self.path_file = os.path.join(self.path_fsaved, self.file_name)
            if self.file_exists and old_file_name != self.file_name:
                #do not rename the file.
                raise StatusError("Cant resume, file name has change. Please retry.")
            self.size_file = self.get_content_size(info) #downloader_core
        else:
            self.limit_exceeded = pb.limit_exceeded
            raise StatusError(pb.err_msg)
    
    def __get_filename_from_source(self, info):
        """"""
        #TODO: validate file name (remove forbidden characters)
        file_name = None
        if info.getheader("Content-Disposition", None): #Content-Disposition: Attachment; filename=name.ext
            disposition = misc.html_entities_parser(info.getheader("Content-Disposition")) #get file name
            if 'filename="' in disposition:
                file_name = disposition.split('filename=')[-1].split('"')[1]
            elif "filename='" in disposition:
                file_name = disposition.split('filename=')[-1].split("'")[1]
            elif 'filename=' in disposition:
                file_name = disposition.split('filename=')[-1]
            elif 'filename*=' in disposition:
                file_name = disposition.split("'")[-1]
        if not file_name: #may be an empty string or None
            file_name = misc.html_entities_parser(self.source.url.split("/")[-1])
        return misc.smartdecode(urllib.unquote_plus(file_name)) #in case its given quoted. smartdecode return utf-8 string
    
    def wait_func(self, wait=0):
        """
        Non-blocking wait (thread-sleep).
        """
        while True:
            if self.stop_flag or self.error_flag:
                return True
            elif not wait: # 0 = False = None
                return False
            time.sleep(1) #segundos
            wait -= 1
            status = "{0}: {1}".format("Wait", misc.time_format(wait))
            self.status_msg = status
    
    def __validate_source(self):
        """"""
        #TODO: check if it is trying to download a html file.
        pass
    
    def __download(self):
        """"""
        if self.resuming and self.file_exists and self.content_range > 0:
            mode = "r+b" #leer y escribir en la posicion deseada con seek.
        else:
            mode = "wb"
            del self.chunks[:]
        
        try:
            with open(self.path_file, mode, cons.FILE_BUFSIZE) as fh: #archivo en donde se escribira lo que se va leyendo del archivo mientras se descarga.
                self.start_time = time.time()
                self.status_msg = "Running"
                self.threaded_download_manager(fh)
                fh.flush() #ensures data is write to disk.
                os.fsync(fh.fileno())
                if self.stop_flag: #set status
                    raise StatusStopped("Stopped")
                elif self.error_flag:
                    raise StatusError(self.status_msg)
                else:
                    self.status, self.status_msg = cons.STATUS_FINISHED, "Finished"
        except EnvironmentError as err:
            logger.exception(err)
            raise StatusError(err)

    def get_remain(self):
        """"""
        try:
            remain_time = ((time.time() - self.start_time) / self.size_complete) * (self.size_file - self.size_complete)
        except ZeroDivisionError:
            return 0
        if remain_time < 0:
            return 0
        else:
            return remain_time
    
    def get_time(self):
        """"""
        if self.start_time > 0:
            return time.time() - self.start_time #elapsed time
        else:
            return 0
    
    def get_progress(self):
        """"""
        try:
            progress = int((self.size_complete * 100) / self.size_file) #porcentaje completado
        except ZeroDivisionError:
            return 0
        if progress > 100:
            return 100
        else:
            return progress
    
    def get_speed(self):
        """"""
        speed = 0
        elapsed_time = time.time() - self.sp_time
        size_complete = self.size_complete #or use lock.
        size = size_complete - self.sp_size
        if size > 0: #si se ejecuta este metodo antes de que se baje el proximo segmento, size = 0 y por ende speed = 0 (asi que no actualizar en ese caso)
            speed = float(size) / elapsed_time #floated speed.
            self.sp_time = time.time()
            self.sp_size = size_complete
        self.sp_deque.append(speed)
        deque_speeds = [last_speed for last_speed in self.sp_deque if int(last_speed) > 0]
        try:
            speed = sum(deque_speeds) / len(deque_speeds)
        except ZeroDivisionError:
            return 0
        if not self.start_time or self.status == cons.STATUS_FINISHED or self.stop_flag or self.error_flag:
            return 0
        return speed


if __name__ == "__main__":
    pass
    
    
    
    
