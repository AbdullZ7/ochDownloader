import os
import collections #usado en get_speed con deque. http://docs.python.org/library/collections.html

import core.cons as cons


class DownloaderCore:
    """"""
    def __init__(self, file_name, path_to_save, link, host, bucket): #bucket = instancia de algoritmo para limitar la banda. get_source = metodo de plugin_bridge
        """"""
        self.stop_flag = False
        self.error_flag = False
        self.host = host
        self.link = link
        self.source = None
        self.link_file = None
        self.file_name = file_name
        self.path_to_save = path_to_save
        self.status = cons.STATUS_RUNNING #status: Running, stopped, Queue, finished.
        self.status_msg = "Connecting"
        self.size_file = 0
        self.size_complete = 0
        self.start_time = 0
        self.file_exists = False
        self.limit_exceeded = False
        
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

    def get_content_size(self, info):
        """"""
        try:
            size_file = int(info.getheader("Content-Length", 0)) #tamanio a bajar restante.
        except ValueError:
            size_file = 0
        if info.getheader("Content-Range", None): #resumir?
            try:
                tmp = int(info["Content-Range"].split("/")[-1])
            except ValueError:
                pass
            else:
                size_file = tmp
        return size_file

    def is_valid_range(self, source, start_range):
        info = source.info()
        if not start_range: #start_range = 0, nothing to do here.
            return True
        elif info.getheader("Content-Range", None) and self.size_file == self.get_content_size(info):
            try:
                print info["Content-Range"]
                range = int(info["Content-Range"].split("/")[0].strip().split(" ")[-1].split("-")[0])
                if range == start_range:
                    return True
            except ValueError:
                pass
        return False