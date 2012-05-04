import urllib2
import urllib
import httplib #para excepciones. httplib.HTTPException
import socket
import traceback
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Local Libs
import core.cons as cons
from core.config import config_parser
from core.lib import socks


class SmartRedirectHandler(urllib2.HTTPRedirectHandler): #subclass
    """
    Extendins HTTPRedirectHandler for better error handling.
    """
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
                                                            self, req, fp, code, msg, headers)
        #new attribute
        result.status = code #= 302, we now can call (URLOpen.)open.status
        return result


_default_socket = socket.socket #singleton var.

class URLOpen:
    """"""
    def __init__(self, cookie=None):
        """"""
        #socket.socket = _default_socket
        proxy_dict = None #system proxy (default)
        if config_parser.get_proxy_active():
            proxy_ip, proxy_port, proxy_type = config_parser.get_proxy()
            #if proxy_type == cons.PROXY_HTTP:
            proxy_dict = {"http": ":".join((proxy_ip, str(proxy_port)))}
            #else: #socks
                #if proxy_type == cons.PROXY_SOCKS5:
                    #proxy_socks_type = socks.PROXY_TYPE_SOCKS5
                #else: #socks 4
                    #proxy_socks_type = socks.PROXY_TYPE_SOCKS4
                #socks.setdefaultproxy(proxy_socks_type, proxy_ip, proxy_port)
                #socket.socket = socks.socksocket
        #elif config_parser.get_system_proxy_active():
            #proxy_dict = {}
            
        #logger.debug(proxy_dict)
        self.opener = urllib2.build_opener(SmartRedirectHandler(),
                                                            urllib2.HTTPHandler(debuglevel=0),
                                                            urllib2.HTTPSHandler(debuglevel=0),
                                                            urllib2.HTTPCookieProcessor(cookie),
                                                            urllib2.ProxyHandler(proxy_dict)) #HTTPCookieProcessor es un handler, pasado a build_opener. Para get y post usar el handler: HTTPHandler
    
    def open(self, url, form=None, data=None, headers=None, range=(None, None), keep_alive=False, referer=None, time_out=20):
        """"""
        url = urllib.quote_plus(url.strip(), safe="%/:=&?~#+!$,;'@()*[]") #fix url. replace spaces by plus sign and more. Solved on python 2.7+
        headers_ = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1",
                    "Accept": "*/*",
                    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                    "Accept-Language": "en-US,en",
                    "Connection": "close"}
                    #"Connection": "keep-alive"}
        range_start, range_end = range
        if headers:
            headers_.update(headers) #overwrite duplicated keys.
        if range_end is not None:
            headers_["Range"] = "bytes={0}-{1}".format(range_start, range_end)
        elif range_start is not None:
            headers_["Range"] = "bytes={0}-".format(range_start)
        if referer is not None:
            headers_["Referer"] = referer
        if form is not None: #may be empty (ex: urllib.urlencode({})).
            headers_["Content-type"] = "application/x-www-form-urlencoded"
        #if form is not None:
        return self.opener.open(urllib2.Request(url, data, headers_), form, timeout=time_out)
        #else:
            #return self.opener.open(urllib2.Request(url, None, headers_), timeout=time_out) #timeout: socket time out.


class URLClose:
    """
    Enhanced closing.
    #Uso:
        #try:
        #        with URLClose(URLOpen().open(link_file)) as s:
        #            source = s
        #    except urllib2.URLError as e:
        #        err = e
        #        source = None #??
        #        print"except"
    """
    def __init__(self, thing, always_close=True):
        self.thing = thing
        self.always_close = always_close
    def __enter__(self): #"yield"
        return self.thing
    def __exit__(self, type, value, traceback):
        if traceback: #se lanzo una exception.
            self.thing.close()
            return False #re-lanzar exception.
        elif self.always_close:
            self.thing.close()


if __name__ == "__main__":
    """
    def set_proxy(proxy_ip, port="0"):
        if proxy_ip:
            http_proxy = ":".join((proxy_ip, port)) #eg: 127.0.0.0:8080
            self.proxy_dict = {"http": http_proxy}
            logger.info("Proxy setted: {0}".format(http_proxy))
        else:
            self.proxy_dict = None
            logger.info("Not using proxy")
            
    proxy_ip = "proxy.alu.uma.es"
    port = "3128"
    set_proxy(proxy_ip, port)
    some = URLOpen
    print some().open("http://cualesmiip.com").read()
    
    url = "http://www.cualesmiip.com"
    some = URLOpen("24.126.223.66", 1734)
    s = some.open(url)
    s.read()

    some = URLOpen("24.126.223.66", 1734, False)
    s = some.open(url)
    print s.read()
    
    form = urllib.urlencode({})
    if form:
        print "some"
    """
    
    url = "http://murl.mobi/headers.php"
    some = URLOpen()
    s = some.open(url)
    print s.read()
    
