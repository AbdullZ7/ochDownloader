import os
import collections #usado en get_speed con deque. http://docs.python.org/library/collections.html

import core.cons as cons


class DownloaderCore:
    """"""
    def __init__(self, file_name, path_fsaved, link, host, bucket): #bucket = instancia de algoritmo para limitar la banda. get_source = metodo de plugin_bridge
        """"""
        self.stop_flag = False
        self.error_flag = False
        self.host = host
        self.link = link
        self.source = None
        self.link_file = None
        self.path_fsaved = path_fsaved #ruta donde se salvara el archivo
        self.file_name = file_name #nombre de archivo.
        self.path_file = os.path.join(self.path_fsaved, self.file_name) #ruta completo al archivo que se descargara
        self.status = cons.STATUS_RUNNING #status: Running, stopped, Queue, finished.
        self.status_msg = "Connecting"
        self.size_file = 0 #tamanio del archivo, se sacara del content-length
        self.size_complete = 0
        self.start_time = 0
        self.file_exists = False
        
        #get_speed stuff
        self.sp_size = 0
        self.sp_time = 0
        self.sp_deque = collections.deque([], 5) #deque = ring_list-like, inicializado con lista/iterable vacia.
        self.old_rate = bucket.fill_rate
        
        self.cookie = None
        self.is_premium = False
        
        #rate limit
        self.bucket = bucket #instancia de clase TokenBucket
        
        #url_parser
        self.content_range = 0
        self.can_resume = False
        self.resuming = False

    def get_content_size(self, info):
        """"""
        size_file = int(info.getheader("Content-Length", 0)) #tamanio a bajar restante.
        if info.getheader("Content-Range", None): #resumir?
            self.can_resume = True
            self.resuming = True
            try:
                size_file = int(info["Content-Range"].split("/")[-1])
            except ValueError:
                size_file = 0
        elif info.getheader("Accept-Ranges", None): #is not None:
            if info["Accept-Ranges"].lower() == "bytes":
                self.can_resume = True
        return size_file


