import subprocess
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons


class Shutdown:
    """"""
    def start_shutting(self):
        """"""
        try:
            if cons.OS_WIN:
                retcode = subprocess.call(["shutdown.exe", "-f", "-s"])
            else:
                retcode = subprocess.call(["sudo", "-n", "shutdown", "-h", "now"])
            if retcode >= 0: #all good.
                return True
        except Exception as err:
            logger.exception(err)
        return False






