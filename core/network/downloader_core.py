import collections #http://docs.python.org/library/collections.html

import core.cons as cons


class DownloaderCore:
    """"""
    def __init__(self, file_name, path_to_save, link, host, bucket):
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

        #get_remain time
        self.size_tmp = 0
        
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
            size_file = int(info["Content-Range"].split("/")[-1]) #Content-Range: bytes 0-92244842/92244843
        except (KeyError, ValueError):
            try:
                size_file = int(info["Content-Length"]) #Content-Length: 92244843
            except (KeyError, ValueError):
                size_file = 0
        return size_file

    def is_valid_range(self, source, start_range):
        info = source.info()
        if not start_range: #start_range = 0, nothing to do here.
            return True
        elif info.getheader("Content-Range", None) and self.size_file == self.get_content_size(info):
            try:
                range = int(info["Content-Range"].split("/")[0].strip().split(" ")[-1].split("-")[0]) #Content-Range: bytes 61505536-92244842/92244843
                if range == start_range:
                    return True
            except ValueError:
                pass
        return False