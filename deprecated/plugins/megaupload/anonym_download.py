#python libs
import urllib, urllib2, httplib, socket
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
class RedirectException(Exception): pass


class AnonymDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self): #wait_func: wait method from thread_managed
        """
        TODO: Refactory.
        """
        link_file = None
        err_msg = None
        source = None
        wait = WAITING
        
        try:
            with URLClose(URLOpen().open(self.link)) as s: #Close conection, en caso de except o al terminar de leer.
                for line in s:
                    if 'id="dlbutton"' in line:
                        link_file = line.split('href="')[1].split('"')[0]
                    if "count=" in line:
                        try:
                            wait = int(line.split("=")[1].split(";")[0])
                        except Exception as err:
                            logger.warning(err)
                            wait = WAITING
                if self.wait_func(wait): #wait... if true: download was stopped
                    return link_file, None, err_msg
            if not link_file:
                raise LinkNotFoundException("Link not found")
                
            #file_name = urllib.quote_plus(link_file.split("/")[5]) #reemplazar signos raros en nombre de archivo (no puedo usar el [-1], si el archivo contiene un "/"
            #link_file = "/".join(link_file.split("/")[:5]) + "/" + file_name #crear url completa con el nuevo nombre de archivo.
            with URLClose(URLOpen().open(link_file, range=(self.content_range, None)), always_close=False) as s:
                try:
                    if s.status == 302: #redirect error 302.
                        raise RedirectException("Redirection error")
                except AttributeError as err: #no redirected.
                    source = s
        except urllib2.HTTPError as err:
            if err.code == 503:
                self.set_limit_exceeded(True)
            err_msg = err
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except (LinkNotFoundException, RedirectException) as err:
            #err_msg = "LinkNotFound in {module}".format(module=__name__)
            err_msg = err
            logger.info(err)
        except Exception as err:
            print err
            err_msg = err
            logger.exception(err)
        
        return link_file, source, err_msg #puede ser el objeto archivo o None.

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)

if __name__ == "__main__":
    #test
    #name, size, unit = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    #disposition = 'filename=name'
    #disposition = disposition.split("filename=")[-1].split('"')[-1]
    #print disposition
    #print urllib.quote_plus("http://www.something.com/dir algo/lgo lo%2co?form=foo&bar=foo", safe="%/:=&?~#+!$,;'@()*[]")
    """
    s = "al\xfa_tes_\xf1\xe1\xe9\xed\xf3\xfa.txt"
    s = s.decode('latin-1')
    s = s.encode('utf-8')
    s = s.decode('latin-1')
    s = s.encode("utf-8", "replace")
    print s.decode("utf-8")
    """
    print "  algo \n ".strip()
    print "some"
    #s = s.encode('utf-8', 'replace')
    #s = chr(233) + 'abcd'
    #s = s.decode("latin-1")
    #s = s.decode("utf-8", "replace")
    #s = s.decode("utf-8", "ignore")
    #print s.decode("utf-8")
    #print s.decode("utf-8")
    """
    name, size, unit = AnonymDownload().check_link("http://www.megaupload.com/?d=MBYIS556")
    if name:
        while True:
            link_file, wait = AnonymDownload().add("/home/estecb/Proyecto", "http://www.megaupload.com/?d=MBYIS556", name)
            if link_file:
                break
        print link_file, wait
    else:
        name = "Unknown"
    """
