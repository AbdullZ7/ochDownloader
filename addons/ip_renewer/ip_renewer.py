import subprocess
import threading
import os
import logging
logger = logging.getLogger(__name__)

import core.cons as cons
import core.misc as misc
from core.conf_parser import conf

#Config parser
OPTION_IP_RENEW_SCRIPT_PATH = "ip_renew_script_path"


class IPRenewer:
    """"""
    def is_running(self):
        """"""
        if hasattr(self, 'th') and self.th.is_alive():
            return True
        else:
            return False

    def start_shell_script(self):
        if not self.is_running():
            path = conf.get_addon_option(OPTION_IP_RENEW_SCRIPT_PATH, default="")
            self.th = threading.Thread(group=None, target=self.shell_script, name=None, args=(path, ))
            self.th.start()

    def start_default_ip_renew(self):
        if not self.is_running():
            self.th = threading.Thread(group=None, target=self.ip_renew, name=None)
            self.th.start()

    def shell_script(self, path):
        """"""
        if os.path.isfile(path):
            if cons.OS_WIN:
                try:
                    retcode = misc.subprocess_call([path, ], shell=True)
                except OSError as err:
                    logger.warning(err)

    def ip_renew(self):
        """default ip renewer"""
        if cons.OS_WIN:
            try:
                retcode = misc.subprocess_call(["ipconfig", "/release"])
                retcode = misc.subprocess_call(["ipconfig", "/renew"])
                #if retcode >= 0: #all good.
            except OSError as err:
                logger.warning(err)


if __name__ == "__main__":
    IPRenewer().ip_renew()