#python libs
import urllib, urllib2, httplib, socket #para excepciones. URLError, httplib.HTTPException,socket.error
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import core.cons as cons
from link_checker import LinkChecker
from core.plugins_core import PluginsCore
from core.network.connection import URLOpen, URLClose #leer/abrir urls. And close connection if except raises.
from core.host_accounts import host_accounts


#custom exceptions
class LinkNotFoundException(Exception): pass
class RedirectException(Exception): pass


class PremiumDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self): #get_login son metodos de premium_accounts.py
        """"""
        link_file = None
        err_msg = None
        source = None
        
        cookie = self.get_cookie()
        if cookie: #login success
            try:
                with URLClose(URLOpen(cookie).open(self.link), always_close=False) as s: #Close conection, en caso de except o al terminar de leer.
                    info = s.info()
                    if info.getheader("Content-Type", None):
                        if "text/html" in info.getheader("Content-Type"):
                            for line in s:
                                if 'class="download_premium_but">' in line:
                                    link_file = line.split('href="')[1].split('"')[0]
                                    s.close() #close connection
                                    break
                        else: #direct download.
                            return cookie, s.url, s, err_msg
                if not link_file:
                    raise LinkNotFoundException("Link not found")
                    
                #file_name = urllib.quote_plus(link_file.split("/")[5]) #reemplazar signos raros en nombre de archivo (no puedo usar el [-1], si el archivo contiene un "/"
                #link_file = "/".join(link_file.split("/")[:5]) + "/" + file_name #crear url completa con el nuevo nombre de archivo.
                with URLClose(URLOpen(cookie).open(link_file, range=(self.content_range, None)), always_close=False) as s:
                    try:
                        if s.status == 302: #redirect error 302.
                            raise RedirectException("Redirection error")
                    except AttributeError as err: #no redirected.
                        source = s
            except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
                err_msg = err
            except (LinkNotFoundException, RedirectException) as err:
                #err_msg = "LinkNotFound in {module}".format(module=__name__)
                err_msg = err
                logger.info(err)
            except Exception as err:
                err_msg = err
                logger.exception(err)
        else:
            err_msg = "Megaupload: login error"
            logger.info(err_msg)
            
        return cookie, link_file, source, err_msg #puede ser el objeto archivo o None.

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)
        
    def get_account_status(self, cookie):
        """"""
        try:
            if cookie is not None: #cant connect
                if cookie: #login fail.
                    with URLClose(URLOpen(cookie).open("http://www.megaupload.com")) as s: #Close conection, en caso de except o al terminar de leer.
                        premium = False
                        for line in s:
                            if 'class="stars_' in line:
                                premium = True
                                break
                        if premium:
                            return cons.ACCOUNT_PREMIUM
                        else:
                            return cons.ACCOUNT_FREE
                else:
                    return cons.ACCOUNT_FAIL
            else:
                return cons.ACCOUNT_ERROR
        except (urllib2.URLError, httplib.HTTPException, socket.error) as e:
            return cons.ACCOUNT_ERROR

    def get_cookie(self): #cookie_handler
        """"""
        cookie = host_accounts.get_cookie("http://www.megaupload.com/?c=login", {"login": "1", "redir": "1", "username": self.username, "password": self.password})
        return cookie
