
import threading


__all__ = ["PersistentQueue", "ImmutableQueue"]


class PersistentQueue:
    """
    A queue that never removes the data from the queue, it only replaces it.
    It can only hold one item.
    It will always contain an item in any given moment.
    """
    def __init__(self, item):
        self._rlock = threading.RLock()
        self._item = item

    def get(self):
        with self._rlock:
            item = self._item

        return item

    def put(self, item):
        with self._rlock:
            self._item = item


class ImmutableQueue(PersistentQueue):
    """
    A queue that can only hold immmutable types.
    It's limited to hold one item.
    """
    def _is_immutable(self, item):
        if isinstance(item, (str, int)):
            return True

        if isinstance(item, tuple):
            for i in item:
                if not self._is_immutable(i):
                    return False

            return True

        return False

    def put(self, item):
        if not self._is_immutable(item):
            raise ValueError("The provided item is mutable.")

        super().put(item)