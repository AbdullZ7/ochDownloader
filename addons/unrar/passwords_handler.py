import os
import threading
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons


PWD_FILE_PATH = os.path.join(cons.APP_PATH, "pwd.txt")

#thread safety
_thread_lock = threading.Lock()


class _PasswordsHandler:
    """"""
    def __init__(self):
        """"""
        self.__passwords_set = set() #unique elements, unorderer.
        self.load()
    
    def get_passwords(self):
        """"""
        with _thread_lock:
            return self.__passwords_set.copy()
    
    def add(self, pwd):
        """"""
        with _thread_lock:
            pwd = pwd.strip()
            if pwd:
                self.__passwords_set.add(pwd)
    
    def replace(self, pwd_list):
        """"""
        with _thread_lock:
            self.__passwords_set = {pwd.strip() for pwd in pwd_list if pwd.strip()} #.copy()
    
    def save(self):
        """"""
        try:
            with open(PWD_FILE_PATH, "w", cons.FILE_BUFSIZE) as fh:
                lines = "\n".join(self.__passwords_set)
                fh.write(lines)
        except Exception as err:
            logger.exception(err)
    
    def load(self):
        """"""
        try:
            with open(PWD_FILE_PATH, "r", cons.FILE_BUFSIZE) as fh:
                lines_list = [line.strip() for line in fh.readlines() if line.strip()]
        except Exception as err:
            logger.exception(err)
        else:
            self.__passwords_set = set(lines_list)


#modules are singletons in python :)
passwords_handler = _PasswordsHandler() #make it global.


if __name__ == "__main__":
    some = set([])
    some.add("some")
    print some


