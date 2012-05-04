#python libs
import urllib, urllib2, httplib, socket #para excepciones. URLError, httplib.HTTPException,socket.error
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import cookielib
import json

#Libs
import core.cons as cons
from link_checker import LinkChecker
from core.plugins_core import PluginsCore
from core.network.connection import URLOpen, URLClose #leer/abrir urls. And close connection if except raises.
from core.host_accounts import host_accounts

#CONNECTION_RETRY = 3
WAITING = None
BASE_URL = "http://wupload.com"


class PremiumDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self): #get_login son metodos de premium_accounts.py
        """
        Wupload API. (el link dura poco tiempo activo, asi q no lo usare)
        http://api.wupload.com/link?method=getDownloadLink&u=USER-EMAIL&p=PASSWORD&ids=1234
        
        try:
            tmp = link.split("/file/")[1].split("/")[0]
            link = "%s/file/%s" % (BASE_URL, tmp)
            file_id = link.split("/")[-1].strip("/")
            
            url = "http://api.wupload.com/link?method=getDownloadLink"
            dict_form = {"u": username, "p": password, "ids": file_id}
            
            with URLClose(URLOpen().open(url, urllib.urlencode(dict_form), range=(content_range, None)), always_close=False) as s:
                rsp = s.read()
                rsp_dict = json.loads(rsp)
                link_list = rsp_dict["FSApi_Link"]["getDownloadLink"]["response"]["links"]
                link_dict = link_list[0]
                link_file = link_dict["url"] #http:\/\/s74.wupload.com\/apidownload\/
                link_file = link_file.replace("\\", "")
                #link_file = url + "&u=" + username + "&p=" + password + "&ids=" + file_id
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except Exception as err:
            logger.exception(err)
            err_msg = err
        """
        link_file = None
        err_msg = None
        source = None
        cookie = None
        
        cookie = self.get_cookie()
        try:
            status = cookie._cookies['.wupload.com']['/']['role'].value
        except Exception as err:
            logger.exception(err)
            cookie = None
            status = None
        
        if cookie and status == "premium": #login success
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
        Wupload API.
        """
        try:
            url = "http://api.wupload.com/user?method=getInfo"
            dict_form = {"u": self.username, "p": self.password}
            with URLClose(URLOpen().open(url, urllib.urlencode(dict_form))) as s:
                rsp = s.read()
            rsp_dict = json.loads(rsp)
            #if rsp_dict["FSApi_User"]["getInfo"]["status"] == "success":
            is_premium = rsp_dict["FSApi_User"]["getInfo"]["response"]["users"]["user"]["is_premium"]
            if is_premium:
                return cons.ACCOUNT_PREMIUM
            else:
                return cons.ACCOUNT_FREE
        except KeyError as err:
            return cons.ACCOUNT_FAIL
        except Exception as err:
            #ValueError: json exception.
            logger.exception(err)
        return cons.ACCOUNT_ERROR

    def get_cookie(self): #cookie_handler
        """
        Not requiered by the api.
        """
        url = "http://www.wupload.com/account/login"
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
    print PremiumDownload().get_cookie("username", "password")
    #print PremiumDownload().get_account_status(None, "username", "password")
    #cookie, link_file, source, err_msg = PremiumDownload().add("http://www.wupload.com/file/318495985/Red.Sweater.FlexTime.v1.2.3.MacOSX.Incl.Keymaker-CORE.rar", None, "esttecb@hotmail.com", "teltron")
    #print err_msg
    #print source.read()
    #tmp_cookie = cookielib.Cookie(version=0, name='enc', value="", port=None, port_specified=False, domain='.filesonic.com', domain_specified=False, domain_initial_dot=True, path='/', path_specified=True, secure=False, expires=None, discard=True, comment="eess", comment_url="asadsa", rest={'HttpOnly': None}, rfc2109=False)
    #cookie = cookielib.CookieJar()
    #cookie.set_cookie(tmp_cookie)
    #print cookie._cookies['.filesonic.com']['/']['enc'].comment
