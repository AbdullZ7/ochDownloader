import os
import urllib2
import urllib
import httplib #para excepciones. httplib.HTTPException
import socket
import time #usado en get_speed
import copy
import threading
import logging
logger = logging.getLogger(__name__)

import core.cons as cons
from connection import URLClose, request

from downloader_core import DownloaderCore


BUFFER_SIZE = 8192 #4096 #Downloader class. 4Kb
NT_BUFSIZ = 8 * 1024 #8K. Network buffer.
MAX_CONN = 10 #0 a 4 = 5, >>> if MAX_CONN < len(self.dict_position): MAX_CONN == len(self.dict_position)
DATA_BUFSIZ = 64 * 1024 #64K.
START, END = range(2)


class BadSource(Exception): pass
class CanNotRun(Exception): pass
class IncompleteChunk(Exception): pass


class MultiDownload(DownloaderCore):
    """"""
    def __init__(self, file_name, path_fsaved, link, host, bucket, chunks):
        """
        bucket = instancia de algoritmo para limitar la banda. get_source = metodo de plugin_bridge
        """
        DownloaderCore.__init__(self, file_name, path_fsaved, link, host, bucket)

        #Threading stuff
        self.lock1 = threading.Lock() #lock to write file and modify size_complete attibute.
        self.lock2 = threading.Lock()


        #resume stuff
        try:
            self.chunks = chunks[:] #shallow copy
        except TypeError:
            self.chunks = []

        #beta stuff...
        self.chunks_control = []
        self.lock3 = threading.Lock()

    def get_chunk_n_size(self):
        """"""
        with self.lock2:
            return self.chunks[:], self.size_complete

    # ////////////////////// Beta stuff...

    def spawn_thread(self, fh, i, chunk):
        """"""
        #Requested Range Not Satisfiable, bug.
        #if chunk[1] is None and chunk[0] > 0:
            #chunk = (chunk[0] - 1, None)
        th = threading.Thread(group=None, target=self.thread_download, name=None, args=(fh, i, chunk))
        th.start()
        return th

    def create_chunks(self):
        chunk_size = (self.size_file / MAX_CONN) + (self.size_file % MAX_CONN)
        chunk_size = ((chunk_size / BUFFER_SIZE) + 1) * BUFFER_SIZE #proximo numero al tamanio del chunk que sea multiplo del buffer
        chunks = []
        start = 0
        while True:
            end = start + chunk_size if (start + chunk_size) < self.size_file else None
            chunks.append((start, end))
            start += chunk_size
            if end is None:
                break
        return chunks

    def __get_chunks_size_complete(self):
        complete = 0
        tmp = 0
        for chunk_tup in self.chunks:
            complete += chunk_tup[START] - tmp
            tmp = chunk_tup[END]
        return complete

    def threaded_download_manager(self, fh):
        """"""
        if not self.chunks or not self.file_exists:
            self.chunks = self.create_chunks()
        else: #resume
            self.size_complete = self.__get_chunks_size_complete()

        self.chunks_control = [True for _ in self.chunks] #can_run

        th_list = [self.spawn_thread(fh, i, chunk) for i, chunk in enumerate(self.chunks[:])]
                   #if chunk[1] is None or chunk[0] < chunk[1]] #range_start may be bigger than range_end at the end by 1 byte (1025, 1024) coz it starts on 0.

        for th in th_list:
            th.join()

    def is_master(self, chunk): #or pass is_master to thread_download
        master = True if chunk[START] == self.content_range else False
        return master

    def is_valid(self, source):
        info = source.info()
        if self.size_file == self.get_content_size(info):
            return True
        return False

    def is_chunk_complete(self, chunk, complete):
        return True

    def get_source(self, chunk, complete):
        if self.is_master(chunk):
            return self.source
        else:
            return request.get(self.link_file, cookie=self.cookie, range=(chunk[0] + complete, None))

    def thread_download(self, fh, i, chunk):
        #master thread wont retry.
        #is_downloading = False
        is_master = self.is_master(chunk)
        buffer_list = []
        len_buffer_data = 0
        complete = 0
        def flush_buffer():
            buf_data = ''.join(buffer_list)
            try:
                with self.lock1:
                    #flush buffer
                    fh.seek(chunk[START] + complete - len_buffer_data)
                    fh.write(buf_data)
                with self.lock2:
                    self.chunks[i] = (chunk[START] + complete, self.chunks[i][END])
                del buffer_list[:]
            except EnvironmentError as err:
                logger.exception(err)
                self.error_flag = True
                self.status_msg = "Error: {0}".format(err)

        #for retry in range(3):
        try:

            with URLClose(self.get_source(chunk, complete)) as s:
                if not self.is_master(chunk) and not self.is_valid(s):
                    raise BadSource('Link expired, or cant download the requested range.')

                with self.lock3:
                    if self.chunks_control[i]:
                        self.chunks_control[i] = False
                        #is_downloading = True
                    else: #elif not is_downloading: #may be retrying
                        raise CanNotRun('Another thread has taken over this chunk.')

                while True:
                    data = s.read(NT_BUFSIZ)
                    len_data = len(data)

                    buffer_list.append(data)
                    len_buffer_data += len_data
                    complete += len_data

                    if len_buffer_data >= DATA_BUFSIZ:
                        flush_buffer()
                        len_buffer_data = 0

                    with self.lock2:
                        self.size_complete += len_data

                    if self.stop_flag or self.error_flag:
                        return

                    if not len_data or (chunk[END] is not None and complete >= chunk[END] - chunk[START]):
                    #if not self.is_chunk_complete(chunk, complete):
                    #raise IncompleteChunk('Incomplete chunk')
                        with self.lock2: #safe.
                            with self.lock3:
                                try:
                                    i_ = i + 1
                                    if self.chunks_control[i_] and chunk[END] == self.chunks[i_][START]: #on resume, end from the current segment must be equal to start from the next one.
                                        chunk = (chunk[START], self.chunks[i_][END]) #in case chunk[START] > self.chunks[i_][START] ?
                                        self.chunks_control[i_] = False
                                    elif not self.chunks_control[i_]:
                                        raise CanNotRun('Can not resume next chunk')
                                    else:
                                        return
                                except IndexError:
                                    return
                                else:
                                    i += 1

        except IncompleteChunk as err:
            #master included
            #propagate
            logger.exception(err)
            self.error_flag = True
            self.status_msg = "Error: {0}".format(err)
            return
        except (BadSource, CanNotRun) as err:
            #not master
            #do not propagate
            logger.debug(err)
            return
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            if is_master:
                #propagate
                logger.warning(err)
                self.error_flag = True
                self.status_msg = "Error: {0}".format(err)
            else:
                logger.debug(err)
                #retry
            return
        except EnvironmentError as err:
            #propagate
            logger.exception(err)
            self.error_flag = True
            self.status_msg = "Error: {0}".format(err)
            return
        finally:
            flush_buffer()


if __name__ == "__main__":
    my_local = 1
    def some():
        global my_local
        my_local = 2
    some()
    print my_local
