import subprocess
import threading
import time
import os
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons


class IPRenewer:
    """"""
    def __init__(self):
        """"""
        self.__th = None
    
    def is_alive(self):
        """"""
        try:
            if self.__th.is_alive():
                return True
        except AttributeError:
            pass
        return False
    
    def start(self, script_path=None):
        """"""
        if not self.is_alive():
            if script_path is not None:
                self.__th = threading.Thread(group=None, target=self.start_shell_script, name=None, args=(script_path, ))
                self.__th.start()
            else:
                self.__th = threading.Thread(group=None, target=self.ip_renew, name=None)
                self.__th.start()
            return True
        else:
            return False
    
    def start_shell_script(self, script_path):
        """"""
        if os.path.isfile(script_path):
            if cons.OS_WIN:
                try:
                    retcode = subprocess.call([script_path, ], shell=True)
                except OSError as err:
                    logger.warning(err)
    
    def ip_renew(self):
        """default ip renewer"""
        if cons.OS_WIN:
            try:
                logger.info("IP renew.")
                retcode = subprocess.call(["ipconfig", "/release"])
                retcode = subprocess.call(["ipconfig", "/renew"])
                #if retcode >= 0: #all good.
            except OSError as err:
                logger.warning(err)


if __name__ == "__main__":
    IPRenewer().ip_renew()
