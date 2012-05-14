import os
import urllib2
import urllib
import httplib #para excepciones. httplib.HTTPException
import socket
import time #usado en get_speed
import copy
import threading
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from connection import URLOpen, URLClose

from downloader_core import DownloaderCore


BUFFER_SIZE = 8192 #4096 #Downloader class. 4Kb
NT_BUFSIZ = 8 * 1024 #8K. Network buffer.
MAX_CONN = 10 #0 a 4 = 5, >>> if MAX_CONN < len(self.dict_position): MAX_CONN == len(self.dict_position)
DATA_BUFSIZ = 64 * 1024 #64K.


class ChunkComplete(Exception): pass
class BadSource(Exception): pass
class CanNotRun(Exception): pass


class MultiDownload(DownloaderCore):
    """"""
    def __init__(self, file_name, path_fsaved, link, host, bucket, chunks): #bucket = instancia de algoritmo para limitar la banda. get_source = metodo de plugin_bridge
        """"""
        DownloaderCore.__init__(self, file_name, path_fsaved, link, host, bucket)

        #Threading stuff
        self.lock1 = threading.Lock() #lock to write file and modify size_complete attibute.
        self.lock2 = threading.Lock()


        #resume stuff
        #NO HACER self.dict_position = dict_position porq tendrian la mismas referencias (si uno cambia el otro tmb)
        #self.dict_chunks = dict_chunks.copy() #{conn_num: [int_start, int_end], } dict.copy() shallow copy es seguro solo para objetos inmutables (string, int) no listas, referencias a clases, etc.
        #self.dict_chunks = copy.deepcopy(dict_chunks)
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

    def spawn_thread(self, fh, i, chunks_tuple):
        """"""
        #Requested Range Not Satisfiable, bug.
        if chunks_tuple[1] is None and chunks_tuple[0] > 0:
            chunks_tuple = (chunks_tuple[0] - 1, None)
        th = threading.Thread(group=None, target=self.thread_download, name=None, args=(fh, i, chunks_tuple))
        th.start()
        return th

    def create_chunks(self):
        chunk_size = (self.size_file / MAX_CONN) + (self.size_file % MAX_CONN)
        chunk_size = ((chunk_size / BUFFER_SIZE) + 1) * BUFFER_SIZE #proximo numero al tamanio del chunk que sea multiplo del buffer
        chunks = []
        start = 0
        while True:
            end = start + chunk_size if (start + chunk_size) < self.size_file else None #start + chunk_size - 1 to avoid overlapping
            chunks.append((start, end))
            start += chunk_size
            if end is None:
                break
        return chunks

    def __get_chunks_size_complete(self):
        complete = 0
        tmp = 0
        for chunk_tup in self.chunks:
            complete += chunk_tup[0] - tmp
            tmp = chunk_tup[1]
        return complete

    def threaded_download_manager(self, fh):
        """"""
        if not self.chunks or not self.file_exists:
            self.chunks = self.create_chunks()
        else: #resume
            self.size_complete = self.__get_chunks_size_complete()

        self.chunks_control = [True for _ in self.chunks] #can_run

        th_list = [self.spawn_thread(fh, i, chunks_tuple) for i, chunks_tuple in enumerate(self.chunks[:])
                   if chunks_tuple[1] is None or chunks_tuple[0] < chunks_tuple[1]] #range_start may be bigger than range_end at the end by 1 byte (1025, 1024) coz it starts on 0.

        for th in th_list:
            th.join()

    def is_master(self, chunk): #or pass is_master to thread_download
        master = True if chunk[0] == self.content_range else False
        return master

    def is_valid(self, source):
        info = source.info()
        if self.size_file == self.get_content_size(info):
            return True
        return False


    def get_source(self, chunk):
        #if self.is_master():
            #source = self.source
        source = self.source
        return source

    def thread_download_(self, fh, i, chunk):
        #master thread wont retry.
        buffer_list = []
        len_buffer_data = 0
        complete = 0
        def flush_buffer():
            buf_data = ''.join(buffer_list)
            try:
                with self.lock1:
                    fh.seek(chunk[0] + complete - len_buffer_data)
                    fh.write(buf_data)
                with self.lock2:
                    start = chunk[0] + complete
                    self.chunks[i] = (start, self.chunks[i][1])
                del buffer_list[:]
                len_buffer_data = 0
            except EnvironmentError as err:
                logger.exception(err)
                self.error_flag = True
                self.status_msg = "Error: {0}".format(err)

        for retry in range(3):
            try:

                with URLClose(self.get_source(chunk)) as s:
                    if not self.is_master(chunk) and not self.is_valid(s):
                        raise BadSource('Link expired, or cant download the requested range.')

                    with self.lock3:
                        if self.chunks_control[i]:
                            self.chunks_control[i] = False
                        else:
                            raise CanNotRun('Another thread has taken over this chunk.')

                    while True:
                        data = s.read(NT_BUFSIZ)
                        len_data = len(data)

                        buffer_list.append(data)
                        len_buffer_data += len_data
                        complete += len_data

                        if len_buffer_data >= DATA_BUFSIZ:
                            flush_buffer()

                        with self.lock2:
                            self.size_complete += len_data

                        if complete >= chunk[1] - chunk[0]:
                            i += 1
                            with self.lock2: #safe.
                                with self.lock3:
                                    try:
                                        if self.chunks_control[i] and chunk[1] == self.chunks[i][0]: #on resume, end from the current segment must be equal to start from the next one.
                                            chunk = self.chunks[i]
                                            self.chunks_control[i] = False
                                        #elif self.chunks_control[i]:
                                            #raise CantResume('cant resume next chunk')
                                        else:
                                            return
                                    except IndexError:
                                        return
                            complete = 0
                            len_buffer_data = 0




            except (BadSource, CanNotRun) as err:
                #not master
                #propagate
                return
            except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
                #if self.is_master():
                    #propagate
                #else:
                    #retry
                return
            except EnvironmentError as err:
                #propagate
                return
            finally:
                flush_buffer()


    def thread_download(self, fh, i, chunk_range):
        print "beta"
        complete = 0
        running_flag = False
        while True:
            try:
                #if not is_resuming: self.content_range = 0
                if chunk_range[0] == self.content_range and not running_flag:
                    s = self.source
                    running_flag = True
                else:
                    with URLClose(URLOpen(self.cookie).open(self.link_file, range=(chunk_range[0] + complete, None)), always_close=False) as source:
                        s = source
                with URLClose(s) as source:
                    info = source.info()
                    if self.size_file != self.get_content_size(info): #and content-len != self.size_file
                        if running_flag:
                            raise EnvironmentError("Link expired, or cant download the requested range.")
                            #print "Link expired, or cant download the requested range."
                        else:
                            return

                    with self.lock3:
                        if self.chunks_control[i]: #can run?
                            self.chunks_control[i] = False
                            running_flag = True
                        elif not running_flag:
                            return

                    while True:
                        while True:
                            data = source.read(BUFFER_SIZE)
                            with self.lock1:
                                fh.seek(chunk_range[0] + complete)
                                fh.write(data)
                            with self.lock2:
                                self.size_complete += len(data)
                                self.chunks[i] = (chunk_range[0] + complete + len(data), self.chunks[i][1])
                            complete += len(data)
                            if self.stop_flag or self.error_flag: #len(data) == 0
                                return
                            if not len(data) or (chunk_range[1] and complete >= (chunk_range[1] - chunk_range[0])): #should be equal.
                                logger.debug("{0}, {1}".format(complete, chunk_range[1] - chunk_range[0] if chunk_range[1] else self.size_file - chunk_range[0]))
                                break

                                #buffer_size = global_buffer_size
                                #if complete >= (chunk_range[1] - chunk_range[0] + buffer_size):
                                #buffer_size = lo q resta.

                                #content_len = 0
                                #if chunk_range[1] is not None:
                                #content_len = chunk_range[1] - chunk_range[0] # + 1
                                #print content_len, complete #error
                                #elif self.size_file and self.size_file > chunk_range[0]:
                                #content_len = self.size_file - chunk_range[0]
                                #print content_len, complete #error
                                #if content_len and content_len > complete:
                                #print content_len, complete #error
                                #raise EnvironmentError("Incomplete chunk")

                        i += 1
                        with self.lock2: #safe.
                            with self.lock3:
                                try:
                                    if self.chunks_control[i] and self.chunks[i][0] == chunk_range[1] : #on resume, end from the current segment must be equal to start from the next one.
                                        self.chunks_control[i] = False
                                    else:
                                        return
                                except IndexError:
                                    return
                            chunk_range = self.chunks[i]
                        complete = 0

            except Exception as err: #excepciones en Threads no pueden ser delegadas.
                logger.exception(err)
                self.error_flag = True
                self.status_msg = "Error: {0}".format(err) #operaciones atomicas. No necesita lock.
                return
            else:
                return

if __name__ == "__main__":
    chunks = [(0, 10), (30, None), (30, 30), (10, 30)]
    print sorted(chunks)
    chunks_ = [chunks_tuple for chunks_tuple in chunks if chunks_tuple[0] != chunks_tuple[1]]
    print sorted(chunks_)

    chunk_size = (self.size_file / MAX_CONN) + (self.size_file % MAX_CONN)
    chunk_size += (chunk_size % BUFFER_SIZE) #multipo del buffer
    lock3 = threading.Lock()
    chunks_control = [(False, True) for _ in self.chunks] #(running, can_run)

    def thread_download(fh, i, chunks_tuple):
        complete = 0
        is_running = False
        while True:
            try:
                with URLOpen(link, range=(chunks_tuple[0], None)) as source:
                    with lock3:
                        if chunks_control[i][1]: #can run?
                            chunks_control[i] = (True, False)
                            is_running = True
                        elif not is_running:
                            return
                    while True:
                        while True:
                            data = source.read(BUFFER_SIZE)
                            with lock1:
                                fh.write(data)
                            with lock2:
                                self.chunks[i] = (chunk_range[0]+complete, self.chunks[i][1])
                            complete += len(data)
                            if not len(data) or complete >= chunks_tuple[1]:
                                break
                        with lock3:
                            i += 1
                            if i > len(chunks_control) - 1: #no more chunks.
                                return
                            if chunks_control[i][1]: #can run?
                                chunks_control[i] = (True, False)
                            else:
                                return

                        with self.lock2:
                            chunk_range = self.chunks[i]
            except:
                return
