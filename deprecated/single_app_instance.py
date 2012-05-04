import sys, os, errno

import cons

#Not Implemented, yet.
#Windows alternativa, usar mutex.
#Application single istance.


class SingleAppInstance:
    """
    TODO: wont work on a multi-user machine (eg: on session logg-off...). Possible solution: save config, session, and cons.LOCK_FILE on user-mydocs dir.
    """
    def __init__(self):
        """"""
        self.lockfile = cons.LOCK_FILE
        #logging.debug("SingleInstance lockfile: " + self.lockfile)
        if cons.OS_WIN:
            try:
                # file already exists, we try to remove (in case previous execution was interrupted)
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile) #same os.remove
                self.fd =  os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except OSError as e:
                if e.errno == 13:
                    #logging.error("Another instance is already running, quitting.")
                    sys.exit(-1)
                print(e.errno)
                pass
        else: # non Windows
            try:
                import fcntl
            except ImportError as err:
                pass
            else:
                try:
                    self.fp = open(self.lockfile, 'w')
                    fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    #logging.warning("Another instance is already running, quitting.")
                    sys.exit(-1)

    def __del__(self): #called on app close?
        """"""
        if cons.OS_WIN:
            if hasattr(self, 'fd'):
                os.close(self.fd)
                os.unlink(self.lockfile)
