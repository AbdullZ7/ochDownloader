import logging

import unittest
from unittest.mock import patch

from core.check.manager import DownloadCheckerManager
from core.check.item import CheckItem, CheckWorkerItem
from core.check.worker import worker
from core import cons

logging.disable(logging.CRITICAL)


def create_item(**kwargs):
    item = CheckItem("http://url.com")

    if 'status' in kwargs:
        item.status = kwargs['status']

    return item


def create_checking_item():
    item = create_item()
    item = CheckWorkerItem(item)
    item.thread = WorkerThreadMock()
    return item


class WorkerThreadMock:
    def result(self):
        return None, "foo", 0, "bar"

    def done(self):
        return True


class CheckManagerTest(unittest.TestCase):

    def setUp(self):
        self.checker = DownloadCheckerManager()
        self.checker._active_limit = 10

        self.item1 = create_item()
        self.checker.pending_downloads[self.item1.uid] = self.item1

        self.item2_checking = create_checking_item()
        self.item2 = self.item2_checking.item
        self.checker.checking_downloads[self.item2.uid] = self.item2_checking

        self.item3 = create_item()
        self.checker.ready_downloads[self.item3.uid] = self.item3

    def tearDown(self):
        pass

    def test_clear(self):
        self.checker.clear()
        self.assertEqual(len(self.checker.pending_downloads), 0)
        self.assertEqual(len(self.checker.checking_downloads), 0)
        self.assertEqual(len(self.checker.ready_downloads), 0)

    def test_create_item(self):
        item = self.checker.create_item("http://foo.com")
        self.assertEqual(item.status, cons.LINK_CHECKING)
        self.assertEqual(item.name, cons.UNKNOWN)

    def test_add(self):
        item = create_item()
        self.checker.add(item)
        self.assertIn(item.uid, self.checker.pending_downloads)

    def test_start_checking(self):
        with patch('core.utils.concurrent.thread.Future.__init__', return_value=None) as f:
            self.checker.start_checking()
            self.assertNotIn(self.item1.uid, self.checker.pending_downloads)
            self.assertIn(self.item1.uid, self.checker.checking_downloads)
            f.assert_called_with(target=worker, args=(self.item1.plugin, self.item1.url))

    def test_update(self):
        with patch.object(DownloadCheckerManager, 'start_checking', return_value=None) as s:
            res = self.checker.update()
            # TODO: test setted item attributes
            self.assertIn(self.item2, res)
            self.assertNotIn(self.item2.uid, self.checker.checking_downloads)
            self.assertIn(self.item2.uid, self.checker.ready_downloads)
            s.assert_called_with()

    def test_recheck(self):
        with patch.object(DownloadCheckerManager, 'start_checking', return_value=None) as s:
            self.checker.ready_downloads.clear()
            item_alive = create_item(status=cons.LINK_ALIVE)
            item_dead = create_item(status=cons.LINK_DEAD)
            item_error = create_item(status=cons.LINK_ERROR)
            item_unavailable = create_item(status=cons.LINK_UNAVAILABLE)
            self.checker.ready_downloads.update({item_alive.uid: item_alive,
                                                 item_dead.uid: item_dead,
                                                 item_error.uid: item_error,
                                                 item_unavailable.uid: item_unavailable})
            self.checker.recheck()
            self.assertEqual(len(self.checker.ready_downloads), 1)
            self.assertIn(item_alive.uid, self.checker.ready_downloads)

            for item in (item_dead, item_error, item_unavailable):
                self.assertIn(item.uid, self.checker.pending_downloads)
                self.assertEqual(item.status, cons.LINK_CHECKING)

            s.assert_called_with()

    def test_pop(self):
        with patch.object(DownloadCheckerManager, 'start_checking', return_value=None) as s:
            uid_list = [self.item1.uid, self.item2.uid, self.item3.uid]
            res = self.checker.pop(uid_list)
            self.assertListEqual(res, [self.item1, self.item2, self.item3])
            s.assert_called_with()
            self.assertRaises(KeyError, self.checker.pop, ['bad-uid', ])


class CheckItemTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass