from core import cons


class DownloaderBase:
    """"""
    def __init__(self, download_item, bucket):
        """"""
        self.file_name = download_item.name
        self.path = download_item.path
        self.host = download_item.host
        self.link = download_item.link
        self.video_quality = download_item.video_quality
        self.save_as = download_item.save_as
        self.cookie = download_item.cookie
        self.stop_flag = False
        self.error_flag = False
        self.source = None
        self.link_file = None
        self.status = cons.STATUS_RUNNING
        self.status_msg = "Connecting"
        self.size_file = 0
        self.size_complete = 0
        self.start_time = 0
        self.file_exists = False
        self.limit_exceeded = False

        #get_remain time
        self.size_tmp = 0 #size_resume

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