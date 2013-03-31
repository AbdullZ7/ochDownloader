import logging
logger = logging.getLogger(__name__)


class Slots:
    """
    Global slots limiter, just for now.
    """
    def __init__(self, limit=10):
        """"""
        self.__limit = limit
        self.slots = 0
    
    def get_limit(self):
        """"""
        return self.__limit
    
    def set_limit(self, limit=10):
        """"""
        try:
            self.__limit = int(limit)
        except Exception as err:
            logger.exception(err)
    
    def add_slot(self):
        """"""
        if self.slots < self.__limit:
            self.slots += 1
            return True
        return False
    
    def remove_slot(self):
        """"""
        if self.slots > 0:
            self.slots -= 1
            return True
        return False
    
    def available_slot(self):
        """"""
        if self.slots < self.__limit:
            return True
        return False