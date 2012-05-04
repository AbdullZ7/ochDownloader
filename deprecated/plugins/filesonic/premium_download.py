#python libs
import urllib, urllib2, httplib, socket #para excepciones. URLError, httplib.HTTPException,socket.error
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import cookielib

#Libs
import core.cons as cons
from link_checker import LinkChecker
from core.plugins_core import PluginsCore
from core.network.connection import URLOpen, URLClose #leer/abrir urls. And close connection if except raises.
from core.host_accounts import host_accounts

#CONNECTION_RETRY = 3
WAITING = None


class PremiumDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self): #get_login son metodos de premium_accounts.py
        """
        TODO: Usar API.
        """
        link_file = None
        err_msg = None
        source = None
        cookie = self.get_cookie()
        try:
            status = cookie._cookies['.filesonic.com']['/']['role'].value
        except Exception as err:
            logger.exception(err)
            cookie = None
            status = None
        
        if cookie and status == "premium": #login success
            #TODO: check the source is not an html file (like in megaupload), server may be temporarily unavailable.
            try:
                with URLClose(URLOpen(cookie).open(self.link, range=(self.content_range, None)), always_close=False) as s:
                    source = s
                    #link_file = s.url
                    link_file = self.link
            except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
                err_msg = err
        
        return cookie, link_file, source, err_msg #puede ser el objeto archivo o None.

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)
        
    def get_account_status(self, cookie):
        """
        TODO: Usar API.
        """
        try:
            if cookie is not None:
                status = cookie._cookies['.filesonic.com']['/']['role'].value
                if status == "premium": #premium?
                    return cons.ACCOUNT_PREMIUM
                elif status == "free":
                    return cons.ACCOUNT_FREE
                else: #anonymous
                    return cons.ACCOUNT_FAIL
            else:
                return cons.ACCOUNT_ERROR
        except Exception as err:
            logger.exception(err)
            return cons.ACCOUNT_ERROR

    def get_cookie(self): #cookie_handler
        """
        Uso:
        if cookie is not None:
            #connection success
            if cookie:
                #login success
            else:
                #login fail
        else:
            #server down
        """
        #for retry in range(COOKIE_CONNECTION_RETRY):
        url = "http://www.filesonic.com/user/login"
        dict_form = {"email": self.username, "redirect": "/", "password": self.password}
        headers = {"Content-type": "application/x-www-form-urlencoded", "X-Requested-With": "XMLHttpRequest", "Accept:": "application/json"}
        try:
            cookie = cookielib.CookieJar()
            with URLClose(URLOpen(cookie).open(url, urllib.urlencode(dict_form), headers=headers)) as s: #eg: url= login-url, data = {"login": "1", "redir": "1", "username": user, "password", password}
                rsp_json = s.read()
                #print rsp_json
                #try:
                    #dict_json = cjson.decode(rsp_json)
                    #print dict_json["status"]
                #except:
                    #pass
            #status = cookie._cookies['.filesonic.com']['/']['role'].value #anonymous, free or premium
            #if status == "anonymous": #login fail like.
                #return []
        except Exception as err: #this only happen on http error, not bad-login, etc.
            logger.warning(err)
            #host_down = True
        else:
            return cookie
        return None #server down, cant connect.
    

if __name__ == "__main__":
    cookie = PremiumDownload().get_cookie("username", "password")
    print PremiumDownload().get_account_status(cookie, None, None)
    #tmp_cookie = cookielib.Cookie(version=0, name='enc', value="", port=None, port_specified=False, domain='.filesonic.com', domain_specified=False, domain_initial_dot=True, path='/', path_specified=True, secure=False, expires=None, discard=True, comment="eess", comment_url="asadsa", rest={'HttpOnly': None}, rfc2109=False)
    #cookie = cookielib.CookieJar()
    #cookie.set_cookie(tmp_cookie)
    #print cookie._cookies['.filesonic.com']['/']['enc'].comment
