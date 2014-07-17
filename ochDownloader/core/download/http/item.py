import threading
from http import cookiejar

from core import const
from core.utils.queue import ImmutableQueue


class DownloaderItem:

    def __init__(self, item):
        self.name = item.name
        self.path = item.path
        self.video_quality = item.video_quality
        self.chunks = list(item.chunks)
        self.save_as = item.save_as
        self.url = item.url
        self.host = item.host

        self.size = 0
        self.size_complete = 0
        self.start_time = 0
        self.can_resume = False
        self.is_premium = False
        self.status = const.STATUS_RUNNING
        self.message = _("Connecting")

        self.limit_exceeded = False
        self.source = None
        self.url_source = None
        self.cookie = cookiejar.CookieJar()
        self.content_range = 0
        self.conn_count = 0
        self.stop_event = threading.Event()

        self.queue = ImmutableQueue(self._update())

    @property
    def plugin(self):
        return self.host.replace(".", "_")

    def _update(self):
        return (
            self.name,
            self.video_quality,
            tuple(self.chunks),
            self.save_as,
            self.size,
            self.size_complete,
            self.start_time,
            self.can_resume,
            self.is_premium,
            self.status,
            self.message
        )

    def update(self):
        self.queue.put(self._update())

    def is_stopped(self):
        return self.stop_event.is_set()