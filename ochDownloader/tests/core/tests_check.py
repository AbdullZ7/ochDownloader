import logging

import unittest
from unittest.mock import patch, Mock

from core.check.manager import DownloadCheckerManager
from core.check.item import CheckItem, CheckWorkerItem
from core.check.worker import worker
from core import cons

logging.disable(logging.CRITICAL)


def create_item(**kwargs):
    url = kwargs.get('url', "http://url.com")
    item = CheckItem(url)

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
            f.assert_called_once_with(target=worker, args=(self.item1.plugin, self.item1.url))
            self.assertNotIn(self.item1.uid, self.checker.pending_downloads)
            self.assertIn(self.item1.uid, self.checker.checking_downloads)

    def test_update(self):
        with patch.object(DownloadCheckerManager, 'start_checking', return_value=None) as s:
            res = self.checker.update()
            s.assert_called_once_with()
            # TODO: test setted item attributes
            self.assertIn(self.item2, res)
            self.assertNotIn(self.item2.uid, self.checker.checking_downloads)
            self.assertIn(self.item2.uid, self.checker.ready_downloads)

    def test_recheck(self):
        self.checker.ready_downloads.clear()
        item_alive = create_item(status=cons.LINK_ALIVE)
        item_dead = create_item(status=cons.LINK_DEAD)
        item_error = create_item(status=cons.LINK_ERROR)
        item_unavailable = create_item(status=cons.LINK_UNAVAILABLE)
        self.checker.ready_downloads.update({item_alive.uid: item_alive,
                                             item_dead.uid: item_dead,
                                             item_error.uid: item_error,
                                             item_unavailable.uid: item_unavailable})

        with patch.object(DownloadCheckerManager, 'start_checking', return_value=None) as s:
            self.checker.recheck()
            s.assert_called_once_with()
            self.assertEqual(len(self.checker.ready_downloads), 1)
            self.assertIn(item_alive.uid, self.checker.ready_downloads)

            for item in (item_dead, item_error, item_unavailable):
                self.assertIn(item.uid, self.checker.pending_downloads)
                self.assertEqual(item.status, cons.LINK_CHECKING)

    def test_pop(self):
        with patch.object(DownloadCheckerManager, 'start_checking', return_value=None) as s:
            uid_list = [self.item1.uid, self.item2.uid, self.item3.uid]
            res = self.checker.pop(uid_list)
            s.assert_called_once_with()
            self.assertListEqual(res, [self.item1, self.item2, self.item3])
            self.assertRaises(KeyError, self.checker.pop, ['bad-uid', ])


class CheckItemTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_worker_item(self):
        item = create_item()
        w_item = CheckWorkerItem(item)
        self.assertEqual(w_item.item, item)
        self.assertIs(w_item.thread, None)

    def test_item(self):
        with patch('core.check.item.uid', return_value="uid") as u:
            with patch('core.check.item.get_host_from_url', return_value="foo.com") as h:
                item2 = CheckItem(url="http://foo.com")
                self.assertEqual(item2.uid, "uid")
                u.assert_called_once_with()
                h.assert_called_once_with("http://foo.com")
                self.assertEqual(item2.uid, "uid")
                self.assertEqual(item2.url, "http://foo.com")
                self.assertEqual(item2.host, "foo.com")
                self.assertIs(item2.name, None)
                self.assertEqual(item2.size, 0)
                self.assertIs(item2.status, None)
                self.assertIs(item2.message, None)
                self.assertEqual(item2.plugin, "foo_com")

        item1 = create_item()
        self.assertIs(item1.host, None)
        self.assertIs(item1.plugin, None)


class CheckerMock(Mock):

    class Checker(Mock):
        name = "name"
        status = "status"
        size = "size"
        message = "message"

        def parse(self):
            pass


class CheckWorkerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_worker(self):
        with patch('importlib.import_module', new_callable=CheckerMock) as m:
            with patch('core.check.worker.utils.normalize_file_name', return_value="norm-name") as u:
                res = worker("foo_com", "http://foo.com")
                m.assert_called_once_with("plugins.foo_com.checker")
                u.assert_called_once_with("name")
                self.assertEqual(res, ('status', 'norm-name', 'size', 'message'))

        with patch('importlib.import_module', side_effect=Exception("foo!")) as m:
            res = worker("foo_com", "http://foo.com")
            m.assert_called_once_with("plugins.foo_com.checker")
            self.assertEqual(res, (cons.STATUS_ERROR, None, 0, 'foo!'))