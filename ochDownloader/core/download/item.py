import time
import logging
from collections import deque

from core import const
from core.common.item import uid, get_host_from_url

logger = logging.getLogger(__name__)


class ActiveItem:

    def __init__(self, item):
        self.item = item
        self.thread = None
        self.queue = None
        self.stop_event = None

    def update(self):
        i = self.queue.get()
        try:
            (
                self.item.name,
                self.item.video_quality,
                self.item.chunks,
                self.item.save_as,
                self.item.size,
                self.item.size_complete,
                self.item.start_time,
                self.item.can_resume,
                self.item.is_premium,
                self.item.status,
                self.item.message,
                #item.size_resume,
            ) = i
        finally:
            self.queue.put(i, block=False)

        #item.calc_stats()

        # Force status stopped in case there is a "status error"
        if self.is_stopped() and self.item.status == const.STATUS_ERROR:
            self.item.status = const.STATUS_STOPPED

    def stop(self):
        self.stop_event.set()

    def is_stopped(self):
        return self.stop_event.is_set()


class DownloadItem:

    def __init__(self, url, name=None, path=None):
        self.uid = uid()
        self.url = url
        self.host = get_host_from_url(url)
        self.name = name
        self.path = path
        self.size = 0
        self.size_complete = 0
        self.can_resume = False
        self.is_premium = False
        self.status = None
        self.message = None

        self.chunks = tuple()
        self.video_quality = None
        self.save_as = None
        self.fail_count = 0

        self.start_time = 0
        self.size_resume = 0

        self.sp_size = 0
        self.sp_time = 0
        self.sp_deque = deque([], 5)

    @property
    def plugin(self):
        if not self.host:
            return

        return self.host.replace(".", "_")

    def progress(self):
        try:
            progress = int((self.size_complete * 100) / self.size)
        except ZeroDivisionError:
            return 0

        if progress > 100:
            return 100

        return progress

    def speed(self):
        if not self.start_time or self.status != const.STATUS_RUNNING:
            return 0

        size_complete = self.size_complete
        speed = float((size_complete - self.sp_size)) / (time.time() - self.sp_time)  # size / elapsed_time
        self.sp_size = size_complete
        self.sp_time = time.time()
        self.sp_deque.append(speed)
        deque_speeds = [last_speed for last_speed in self.sp_deque if int(last_speed) > 0]

        try:
            speed = sum(deque_speeds) / len(deque_speeds)
        except ZeroDivisionError:
            return 0

        return speed

    def time_remain(self):
        if not self.start_time:
            return 0

        lapse = time.time() - self.start_time
        completed = self.size_complete - self.size_resume
        remain_size = self.size - self.size_complete

        try:
            remain_time = (lapse / completed) * remain_size
        except ZeroDivisionError:
            return 0

        if remain_time < 0:
            return 0

        return remain_time

    def time(self):
        if not self.start_time:
            return 0

        return time.time() - self.start_time