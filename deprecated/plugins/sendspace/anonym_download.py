#python libs
import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from link_checker import LinkChecker
from core.plugins_core import PluginsCore
from core.network.connection import URLOpen, URLClose #leer/abrir urls. And close connection if except raises.

#CONNECTION_RETRY = 3
WAITING = 0

#custom exceptions
class LinkNotFoundException(Exception): pass


class AnonymDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self): #wait_func: wait method from thread_managed
        """"""
        link_file = None
        err_msg = None
        source = None
        wait = WAITING
        
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        form = urllib.urlencode({"download": "Regular Download"})
        
        try:
            with URLClose(URLOpen().open(self.link, form, headers=headers)) as s:
                #print s.read()
                if self.wait_func(): #wait... if true: download was stopped
                    return self.link, None, err_msg
                for line in s:
                    if "download_button" in line:
                        link_file = line.split('href="')[-1].split('"')[0]
            if not link_file:
                raise LinkNotFoundException("Link not found")
            with URLClose(URLOpen().open(link_file, range=(self.content_range, None)), always_close=False) as s:
                source = s
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except LinkNotFoundException as err:
            err_msg = err
            logger.info(err)
        except Exception as err:
            err_msg = err
            logger.exception(err)
        
        return link_file, source, err_msg

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)


if __name__ == "__main__":
    #test
    #name, size, unit = AnonymDownload().check_link("http://rapidshare.com/files/3415371904/WC_0310_HRALinks.info.avi")
    def wait_func():
        return False
    link_file, source, err = AnonymDownload().add("http://www.sendspace.com/file/ww2x92", 0, wait_func)
    print link_file, err
