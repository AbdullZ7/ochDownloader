import os
import threading
import time
import logging
logger = logging.getLogger(__name__)

#Local Libs
from core import cons
from core import utils
from core.conf_parser import conf
from core.plugin.parser import PluginParser

from core.download.multipart import MultiDownload


class StatusError(Exception): pass
class StatusStopped(Exception): pass


class Downloader(threading.Thread, MultiDownload):
    """"""
    def __init__(self, download_item, bucket):
        """"""
        threading.Thread.__init__(self)
        MultiDownload.__init__(self, download_item, bucket)

    def run(self):
        """"""
        try:
            self.__file_existence_check()
            self.__source()
            self.__validate_source()
            self.__set_filename_n_size()
            self.__set_can_resume()
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
        else:
            self.status = cons.STATUS_FINISHED
            self.status_msg = "Finished"
        finally:
            if self.source:
                self.source.close()

    def wait_func(self, wait=0):
        """
        Non-blocking wait (thread-sleep).
        """
        while True:
            if self.stop_flag or self.error_flag:
                return True
            elif not wait:
                return False
            time.sleep(1)
            wait -= 1
            self.status_msg = "{}: {}".format("Wait", utils.time_format(wait))

    def __file_existence_check(self):
        """"""
        START, END = range(2)
        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            elif os.path.isfile(os.path.join(self.path, self.file_name)):
                self.file_exists = True
                start_chunks = [chunk[START] for chunk in self.chunks
                                if chunk[START] < chunk[END]]
                if start_chunks:
                    self.content_range = min(start_chunks)
        except (EnvironmentError, ValueError) as err:
            logger.exception(err)
            raise StatusError(err)
    
    def __source(self):
        """"""
        pb = PluginParser(self.link, self.host, self.video_quality, self.content_range, self.wait_func)
        pb.parse()
        self.source = pb.source
        if self.stop_flag:
            raise StatusStopped("Stopped")
        elif self.source:
            self.link_file = pb.dl_link
            self.cookie = self.cookie or pb.cookie
            self.save_as = self.save_as or pb.save_as
            self.video_quality = pb.video_quality
        else:
            self.limit_exceeded = pb.limit_exceeded
            raise StatusError(pb.err_msg)

    def __set_filename_n_size(self):
        info = self.source.info()
        old_file_name = self.file_name
        if self.save_as:
            self.file_name = utils.normalize_file_name(self.save_as)
        else:
            self.file_name = self.__get_filename_from_source(info)
        if self.file_exists and old_file_name != self.file_name:
            #do not rename the file.
            raise StatusError("Cant resume, file name has change. Please retry.")
        self.size_file = self.get_content_size(info) #downloader_core
    
    def __get_filename_from_source(self, info):
        """"""
        file_name = None
        if info.getheader("Content-Disposition", None): #Content-Disposition: Attachment; filename=name.ext
            disposition = info.getheader("Content-Disposition") #get file name
            if 'filename="' in disposition:
                file_name = disposition.split('filename=')[-1].split('"')[1]
            elif "filename='" in disposition:
                file_name = disposition.split('filename=')[-1].split("'")[1]
            elif 'filename=' in disposition:
                file_name = disposition.split('filename=')[-1]
            elif 'filename*=' in disposition:
                file_name = disposition.split("'")[-1]
        if not file_name: #may be an empty string or None
            file_name = utils.get_filename_from_url(self.source.url)
        elif file_name.startswith('=?UTF-8?B?'): #base64
            file_name = file_name[10:].decode('base64')
        file_name = utils.normalize_file_name(file_name)
        return file_name

    def __set_can_resume(self):
        info = self.source.info()
        if info.getheader("Content-Range", None):
            self.can_resume = True
        elif info.getheader("Accept-Ranges", None):
            if info["Accept-Ranges"].lower() == "bytes":
                self.can_resume = True
    
    def __validate_source(self):
        """"""
        info = self.source.info()
        if not conf.get_html_dl() and "text/html" in info.getheader("Content-Type", ""): #Content-Type: text/html; charset=ISO-8859-4
            raise StatusError("HTML detected.")
    
    def __download(self):
        """"""
        if self.file_exists and self.chunks and self.is_valid_range(self.source, self.content_range):
            mode = "r+b" #resume (with seek)
        else:
            mode = "wb"
            del self.chunks[:]
        
        try:
            with open(os.path.join(self.path, self.file_name), mode, cons.FILE_BUFSIZE) as fh:
                self.start_time = time.time()
                self.status_msg = cons.STATUS_RUNNING
                self.threaded_download_manager(fh)
                fh.flush() #ensures data is write to disk.
                os.fsync(fh.fileno())
                if self.stop_flag:
                    raise StatusStopped("Stopped")
                if self.error_flag:
                    raise StatusError(self.status_msg)
        except EnvironmentError as err:
            logger.exception(err)
            raise StatusError(err)


if __name__ == "__main__":
    pass
    
    
    
    
