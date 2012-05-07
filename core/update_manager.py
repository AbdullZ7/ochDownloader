import time
import threading
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from network.connection import URLClose, request
import cons


class UpdateManager(threading.Thread):
    """"""
    def __init__(self):
        """"""
        threading.Thread.__init__(self) #iniciar threading.Thread
        self.update_check_complete = False
        self.update_available = False
        self.url_update = []
        self.fhash_update = None
        self.manual_update = False
    
    def run(self):
        """"""
        self.start_update()
    
    def start_update(self):
        """"""
        try:
            if cons.OS_WIN:
                update_url = cons.UPDATE_URL
            else:
                update_url = cons.UPDATE_UNIX_URL
            with URLClose(request.get(update_url, time_out=10)) as s:
                for line in s.readlines():
                    line = line.strip()
                    if line.startswith("last:"):
                        last_ver = line.split("last:")[-1].strip()
                        if last_ver != cons.APP_VER:
                            self.update_available = True
                    elif line.startswith("manual:"): #need manual update if app_ver > manual
                        manual = line.split("manual:")[-1].strip()
                        manual = manual.split(".")
                        app_version = cons.APP_VER.split(".")
                        try:
                            for enum, m_digit in enumerate(manual):
                                if m_digit > app_version[enum]: #if true, ask for manual update.
                                    self.manual_update = True
                        except IndexError as err: #better say sorry than ask.
                            pass
                    elif line.startswith("http:"):
                        self.url_update.append(line)
                    elif line.startswith("hash:"): #md5hash line
                        self.fhash_update = line.split("hash:")[-1].strip()
        except Exception as err:
            logger.warning("Update except: {0}".format(err))
        finally:
            self.update_check_complete = True


if __name__ == "__main__":
    """
    th_update_manager = UpdateManager()
    th_update_manager.start()
    print "update complete: {0}".format(th_update_manager.update_check_complete)
    while True:
        if th_update_manager.update_check_complete:
            print "update complete: {0}".format(th_update_manager.update_check_complete)
            break
        else:
            time.sleep(2)
    print "update available: {0}, list: {1}".format(th_update_manager.update_available, th_update_manager.url_update)
    """
    pass
