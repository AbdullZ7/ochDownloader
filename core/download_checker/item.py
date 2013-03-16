import uuid
import time
import logging
logger = logging.getLogger(__name__)
from collections import deque

#Libs
from core import cons


class DownloadItem:
    """"""
    def __init__(self, name, host, link, path=cons.DLFOLDER_PATH, can_copy_link=True):
        """"""
        self.id = str(uuid.uuid1()) #id unico.
        self.name = name
        self.host = host
        self.link = link
        self.path = path
        self.can_copy_link = can_copy_link
        self.status = cons.STATUS_QUEUE
        self.status_msg = None
        self.link_status = cons.LINK_CHECKING
        self.link_status_msg = None
        self.size = 0
        self.size_complete = 0
        self.chunks = []
        self.fail_count = 0
        self.can_resume = False
        self.is_premium = False
        self.video_quality = None
        self.save_as = None
        self.cookie = None

        self.start_time = 0
        self.size_resume = 0

        self.sp_size = 0
        self.sp_time = 0
        self.sp_deque = deque([], 5)

        self.progress = 0
        self.speed = 0
        self.time_remain = 0
        self.time = 0

    def _progress(self):
        """"""
        try:
            progress = int((self.size_complete * 100) / self.size) #porcentaje completado
        except ZeroDivisionError:
            return 0
        if progress > 100:
            return 100
        else:
            return progress

    def _speed(self):
        """"""
        if not self.start_time or self.status in (cons.STATUS_FINISHED, cons.STATUS_STOPPED, cons.STATUS_ERROR):
            return 0
        size_complete = self.size_complete
        speed = float((size_complete - self.sp_size)) / (time.time() - self.sp_time) #size / elapsed_time
        self.sp_size = size_complete
        self.sp_time = time.time()
        self.sp_deque.append(speed)
        deque_speeds = [last_speed for last_speed in self.sp_deque if int(last_speed) > 0]
        try:
            speed = sum(deque_speeds) / len(deque_speeds)
        except ZeroDivisionError:
            return 0
        return speed

    def _time_remain(self):
        """"""
        try:
            remain_time = ((time.time() - self.start_time) / (self.size_complete - self.size_resume)) * (self.size - self.size_complete)
        except ZeroDivisionError:
            return 0
        if not self.start_time or remain_time < 0:
            return 0
        else:
            return remain_time

    def _time(self):
        """"""
        if self.start_time:
            return time.time() - self.start_time #elapsed time
        else:
            return 0

    def recalc_stats(self):
        """"""
        self.progress = self._progress()
        self.speed = self._speed()
        self.time_remain = self._time_remain()
        self.time = self._time()


if __name__ == "__main__":
    pass
    
    
    
