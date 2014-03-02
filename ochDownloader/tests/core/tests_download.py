import logging
from queue import Queue
from threading import Event

import unittest
from unittest.mock import patch, Mock

from core import const
from core.download.item import ActiveItem,DownloadItem

logging.disable(logging.CRITICAL)


class DownloadActiveItemTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_update(self):
        class ConstMock:
            STATUS_ERROR = "status"
            STATUS_STOPPED = "status_stopped"

        item = Mock()
        a_item = ActiveItem(item)
        a_item.queue = Queue(1)
        i = ("name",
             "video_quality",
             "chunks",
             "save_as",
             "size",
             "size_complete",
             "start_time",
             "can_resume",
             "is_premium",
             "status",
             "message")

        with patch.object(a_item, 'is_stopped', return_value=False) as e:
            with patch.object(Queue, 'get', return_value=i) as q_get:
                with patch.object(Queue, 'put') as q_put:
                    a_item.update()
                    e.assert_called_once_with()
                    q_get.assert_called_once_with()
                    q_put.assert_called_once_with(i, block=False)
                    i_item = (item.name,
                              item.video_quality,
                              item.chunks,
                              item.save_as,
                              item.size,
                              item.size_complete,
                              item.start_time,
                              item.can_resume,
                              item.is_premium,
                              item.status,
                              item.message,)
                    self.assertEqual(i_item, i)

                    with patch("core.download.item.const", new_callable=ConstMock):
                        e.return_value = True
                        a_item.update()
                        self.assertEqual(item.status, "status_stopped")

    def test_stop(self):
        item = Mock()
        a_item = ActiveItem(item)
        a_item.stop_event = Event()

        with patch.object(Event, 'set') as e:
            a_item.stop()
            e.assert_called_once_with()

    def test_is_stopped(self):
        item = Mock()
        a_item = ActiveItem(item)
        a_item.stop_event = Event()

        with patch.object(Event, 'is_set', return_value="stopped_event") as e:
            res = a_item.is_stopped()
            e.assert_called_once_with()
            self.assertEqual(res, "stopped_event")


class DownloadItemTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

