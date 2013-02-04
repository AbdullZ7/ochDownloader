import subprocess
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core import cons
from core import utils


class Shutdown:
    """"""
    def start_shutting(self):
        """"""
        try:
            if cons.OS_WIN:
                retcode = utils.subprocess_call(["shutdown.exe", "-f", "-s"])
            else:
                retcode = utils.subprocess_call(["sudo", "-n", "shutdown", "-h", "now"])
            if retcode >= 0: #all good.
                return True
        except Exception as err:
            logger.exception(err)
        return False






