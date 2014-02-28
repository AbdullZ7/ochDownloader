import logging

import unittest
from unittest.mock import patch, Mock

from core import const
from core.dispatch import Signal

logging.disable(logging.CRITICAL)


class SlotMock(Mock):
    def foo(self):
        return True


def func():
    return True


class DispatchTest(unittest.TestCase):

    def setUp(self):
        self.signal = Signal()

    def tearDown(self):
        pass

    def test_connect(self):
        slot_mock = SlotMock()

        with patch('core.dispatch.signal.weak_ref') as r:
            self.signal.connect(func)
            r.assert_called_once_with(func)
            self.assertEqual(len(self.signal.callbacks), 1)
            self.signal.connect(slot_mock.foo)
            r.assert_called_with(slot_mock.foo)
            self.assertEqual(len(self.signal.callbacks), 2)

    def test_disconnect(self):
        weakref_mock = Mock()
        weakref_mock.return_value = func
        self.signal.callbacks.append(weakref_mock)
        self.signal.disconnect(func)
        self.assertEqual(len(self.signal.callbacks), 0)

    def test_connect_disconnect(self):
        # bound method
        slot_mock = SlotMock()
        self.signal.connect(slot_mock.foo)
        self.assertEqual(len(self.signal.callbacks), 1)
        self.signal.disconnect(slot_mock.foo)
        self.assertEqual(len(self.signal.callbacks), 0)

        # class function
        self.signal.connect(SlotMock.foo)
        self.assertEqual(len(self.signal.callbacks), 1)
        self.signal.disconnect(SlotMock.foo)
        self.assertEqual(len(self.signal.callbacks), 0)

        # class
        self.signal.connect(SlotMock)
        self.assertEqual(len(self.signal.callbacks), 1)
        self.signal.disconnect(SlotMock)
        self.assertEqual(len(self.signal.callbacks), 0)

        # function
        self.signal.connect(func)
        self.assertEqual(len(self.signal.callbacks), 1)
        self.signal.disconnect(func)
        self.assertEqual(len(self.signal.callbacks), 0)

    def test_emit(self):
        weakref_mock = Mock()
        func_mock = Mock()
        weakref_mock.return_value = func_mock
        self.signal.callbacks.append(weakref_mock)
        self.signal.emit("foo", bar="bar")
        weakref_mock.assert_called_once_with()
        func_mock.assert_called_once_with("foo", bar="bar")

    def test_emit_dead_ref(self):
        weakref_mock = Mock()
        weakref_mock.return_value = None
        self.signal.callbacks.append(weakref_mock)
        self.signal.emit("foo", bar="bar")
        weakref_mock.assert_called_once_with()
        self.assertEqual(len(self.signal.callbacks), 0)