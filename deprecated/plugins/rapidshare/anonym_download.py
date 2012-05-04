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


class LinkNotFoundException(Exception): pass
class LimitExceededException(Exception): pass


class AnonymDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self): #wait_func: wait method from thread_managed
        """
        TODO: Refactory.
        
        rapidshare api (sub=download): http://images.rapidshare.com/apidoc.txt
        """
        link_file = None
        err_msg = None
        source = None
        wait = WAITING

        SUB_HOST, DL_AUTH, WAIT, MD5 = range(4)
        
        try:
            id = self.link.split("/")[-2]
            file_name = self.link.split("/")[-1]
            #for retry in range(CONNECTION_RETRY):
            api_url = "http://api.rapidshare.com/cgi-bin/rsapi.cgi"
            with URLClose(URLOpen().open("{0}?sub=download&fileid={1}&filename={2}".format(api_url, id, file_name))) as s:
            #with URLClose(URLOpen().open("http://api.rapidshare.com/cgi-bin/rsapi.cgi",  form=urllib.urlencode({"sub": "download", "fileid": id, "filename": file_name})), always_close=True) as s: #Close conection, en caso de except o al terminar de leer.
                for line in s:
                    if "DL:" in line:
                        tmp = line.split("DL:")[-1].split(",")
                        wait = int(tmp[WAIT])
                        link_file = "http://{host}/cgi-bin/rsapi.cgi?sub=download&fileid={id}&filename={filename}&dlauth={auth}".format(host=tmp[SUB_HOST], id=id, filename=file_name, auth=tmp[DL_AUTH])
                if wait > 600: #4 minutes
                    raise LimitExceededException("Limit Exceeded")
                if self.wait_func(wait): #wait... if true: download was stopped
                    return link_file, None, err_msg
            if not link_file:
                raise LinkNotFoundException("Link not found")
            with URLClose(URLOpen().open(link_file), always_close=False) as s:
                source = s
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except (LinkNotFoundException, LimitExceededException) as err:
            if isinstance(err, LimitExceededException):
                self.set_limit_exceeded(True)
            err_msg = err
            logger.info(err)
        except Exception as err:
            err_msg = err
            logger.exception(err)
        
        return link_file, source, err_msg #puede ser el objeto archivo o None.
    
    def check_link(self, link):
        """"""
        return LinkChecker().check(link)


if __name__ == "__main__":
    #test
    #name, size, unit = AnonymDownload().check_link("http://rapidshare.com/files/3415371904/WC_0310_HRALinks.info.avi")
    link_file, source, err, wait = AnonymDownload().add("http://rapidshare.com/files/3415371904/WC_0310_HRALinks.info.avi", None)
    print link_file, err, wait
    
