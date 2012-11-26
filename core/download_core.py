import uuid
import time
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict, deque

#Libs
import cons


class DownloadItem:
    """"""
    def __init__(self, name, host, size, link, path=cons.DLFOLDER_PATH, can_copy_link=True): #ile_name, host, size, link
        """"""
        self.id = str(uuid.uuid1()) #id unico.
        self.path = path
        self.name = name
        self.link = link
        self.host = host
        self.link_status = cons.LINK_CHECKING
        self.link_status_msg = None
        self.status = cons.STATUS_QUEUE #download status
        self.status_msg = None
        self.size = size
        self.size_complete = 0
        self.chunks = []
        self.fail_count = 0
        self.can_resume = False
        self.is_premium = False
        self.can_copy_link = can_copy_link
        self.video_quality = None

        self.start_time = 0
        self.size_resume = 0

        self.sp_size = 0
        self.sp_time = 0
        self.sp_deque = deque([], 5)

    @property
    def progress(self):
        """"""
        try:
            progress = int((self.size_complete * 100) / self.size) #porcentaje completado
        except ZeroDivisionError:
            return 0
        if progress > 100:
            return 100
        else:
            return progress

    @property
    def speed(self):
        """"""
        if not self.start_time:
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
        if self.status in (cons.STATUS_FINISHED, cons.STATUS_STOPPED, cons.STATUS_ERROR):
            return 0
        return speed

    @property
    def time_remain(self):
        """"""
        try:
            remain_time = ((time.time() - self.start_time) / (self.size_complete - self.size_resume)) * (self.size - self.size_complete)
        except ZeroDivisionError:
            return 0
        if remain_time < 0:
            return 0
        else:
            return remain_time

    @property
    def time(self):
        """"""
        if self.start_time:
            return time.time() - self.start_time #elapsed time
        else:
            return 0

    def update(self, name, status, size, size_complete, start_time,
               size_resume, chunks, status_msg, can_resume, is_premium, video_quality):
        """"""
        self.name = name
        self.status = status
        self.status_msg = status_msg
        self.size = size
        self.size_complete = size_complete
        self.start_time = start_time
        self.size_resume = size_resume
        self.chunks = chunks or []
        self.can_resume = can_resume
        self.is_premium = is_premium
        self.video_quality = video_quality

    def reset_fail_count(self):
        """"""
        self.fail_count = 0


class DownloadCore:
    """"""
    def __init__(self):
        """"""
        self.active_downloads = {}
        self.queue_downloads = OrderedDict()
        self.complete_downloads = {}
        self.stopped_downloads = {}

    def reorder_queue(self, id_order_list):
        """
        TODO: only replace the order list in OrderedDict.
        """
        ordered_items_dict = OrderedDict()
        for id_item in id_order_list:
            try:
                ordered_items_dict[id_item] = self.queue_downloads[id_item]
            except KeyError:
                pass
        if len(self.queue_downloads) == len(ordered_items_dict):
            self.queue_downloads.clear()
            self.queue_downloads.update(ordered_items_dict)
        else:
            logger.warning("reorder_queue failed")


if __name__ == "__main__":
    pass
    
    
    
