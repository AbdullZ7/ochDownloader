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
from connection import URLClose, request

from downloader_core import DownloaderCore


BUFFER_SIZE = 8192 #4096 #Downloader class. 4Kb
NT_BUFSIZ = 8 * 1024 #8K. Network buffer.
MAX_CONN = 10 #0 a 4 = 5, >>> if MAX_CONN < len(self.dict_position): MAX_CONN == len(self.dict_position)
DATA_BUFSIZ = 64 * 1024 #64K.


class ChunkComplete(Exception): pass


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

    def get_chunk_n_size(self):
        """"""
        with self.lock2:
            return self.chunks[:], self.size_complete

    def spawn_thread(self, fh, i, chunks_tuple):
        """"""
        #Requested Range Not Satisfiable, bug.
        if chunks_tuple[1] is None and chunks_tuple[0] > 0:
            chunks_tuple = (chunks_tuple[0] - 1, None)
        th = threading.Thread(group=None, target=self.thread_download, name=None, args=(fh, i, chunks_tuple))
        th.start()
        return th

    def threaded_download_manager(self, fh):
        """"""
        if not self.chunks or not self.file_exists:
            chunk_size = (self.size_file / MAX_CONN) + (self.size_file % MAX_CONN)
            chunks_ = []
            start = 0
            while True:
                end = start + chunk_size if (start + chunk_size) < self.size_file else None #start + chunk_size - 1 to avoid overlapping
                chunks_.append((start, end))
                if end is not None:
                    start += chunk_size
                else:
                    break
            self.chunks = chunks_
        else: #resume
            complete = 0
            tmp = 0
            for chunk_tuple in self.chunks:
                complete += chunk_tuple[0] - tmp
                tmp = chunk_tuple[1]
            self.size_complete = complete

        th_list = [self.spawn_thread(fh, i, chunks_tuple) for i, chunks_tuple in enumerate(self.chunks[:])
                    if chunks_tuple[1] is None or chunks_tuple[0] <= chunks_tuple[1]] #range_start may be bigger than range_end at the end by 1 byte (1025, 1024) coz it starts on 0.

        for th in th_list:
            th.join()

    def thread_download(self, fh, i, chunk_range):
        """
        DONE: Thread Safe.
        """
        buffer_list = []
        len_buffer_data = 0
        len_data = 0
        complete = 0
        def flush_buffer():
            buf_data = ''.join(buffer_list)
            with self.lock1:
                fh.seek(chunk_range[0] + complete - len_buffer_data)
                fh.write(buf_data)
            with self.lock2:
                start = chunk_range[0] + complete
                self.chunks[i] = (start, self.chunks[i][1])
            del buffer_list[:]
        
        while True:
            try:
                with URLClose(request.get(self.link_file, cookie=self.cookie, range=(chunk_range[0] + complete, chunk_range[1]))) as source:
                    
                    #if (chunk_range[0] and chunk_range[1] is not None) and (self.size_file != self.get_content_size(source.info()) or source.info().getheader("Content-Range", None) is None):
                    info = source.info()
                    if self.size_file != self.get_content_size(info): #and content-len != self.size_file
                        raise EnvironmentError("Link expired, or cant download the requested range.")
                        #print "Link expired, or cant download the requested range."
                    
                    #if not (chunk_range[0] == 0 and chunk_range[1] is None):
                        #if info.getheader("Content-Range", None) is None: #and content-len + chunk_range[0] != self.size_file
                            #raise EnvironmentError("Content-Range tag is missing.")
                            #print "Cant validate the requested range."
                    
                    #Todo: if the above fails, check content-len + chunk_range[0] != self.size_file
                    #comprobar si la etiqueta content-len no existe al sacar el size_file, ya que quedaria en cero y luego si existe content-range sera distinto.
                    #tomar en cuenta cuando no exista content-len o content-range o ambos.
                    
                    while True:
                        
                        data = source.read(NT_BUFSIZ)
                        len_data = len(data)
                        
                        buffer_list.append(data)
                        len_buffer_data += len_data
                        complete += len_data
                        
                        if len_buffer_data >= DATA_BUFSIZ:
                            flush_buffer()
                            len_buffer_data = 0

                        with self.lock2:
                            self.size_complete += len_data
                        
                        if self.bucket.fill_rate: #self.bucket.fill_rate != 0
                            time.sleep(self.bucket.consume(len_data))
                        
                        if self.stop_flag or self.error_flag: #len(data) == 0
                            flush_buffer()
                            return
                        elif not len_data: #todo: check complete against range requested.
                            flush_buffer()
                            content_len = 0
                            if chunk_range[1] is not None:
                                content_len = chunk_range[1] - chunk_range[0] + 1
                                print content_len, complete #error
                            elif self.size_file and self.size_file > chunk_range[0]:
                                content_len = self.size_file - chunk_range[0]
                                print content_len, complete #error
                            if content_len and content_len > complete:
                                #print content_len, complete #error
                                raise EnvironmentError("Incomplete chunk")
                            return
                    
                    #content_len = int(info.getheader("Content-Length", 0)) #some server send wrong sizes.
                    #if content_len and content_len != complete: #verification
                        #raise EnvironmentError("Incomplete chunk")
                    
            except (urllib2.URLError, httplib.HTTPException, socket.error) as err: #httplib.HTTPException = badstatusline, etc
                #TODO: capturar error "overflow" y dar status error para reiniciar resumiendo.
                logger.warning("Conexion {0}: {1}".format(i, err))
                time.sleep(3) #to avoid overflowing the server.
                if self.stop_flag or self.error_flag:
                    flush_buffer()
                    return
                #dont break, lets retry...
            except EnvironmentError as err: #excepciones en Threads no pueden ser delegadas.
                #FIXME: si la excepcion es por falta de espacio en disco, se tendria q eliminar la ultima pos del chunk
                logger.exception(err)
                self.error_flag = True
                self.status_msg = "Error: {0}".format(err) #operaciones atomicas. No necesita lock.
                return
