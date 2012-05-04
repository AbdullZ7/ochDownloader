#python libs
import urllib, urllib2, httplib, socket
import cookielib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from link_checker import LinkChecker
from core.plugins_core import PluginsCore
from core.network.connection import URLOpen, URLClose #leer/abrir urls. And close connection if except raises.
from addons.captcha.recaptcha import Recaptcha

#CONNECTION_RETRY = 3
BASE_URL = "http://filefactory.com"
WAITING = 60


class FileLinkFoundException(Exception): pass
class CaptchaException(Exception): pass
class LinkNotFoundException(Exception): pass
class LimitExceededException(Exception): pass
class RedirectException(Exception): pass


class AnonymDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self):
        """"""
        link_file = None
        err_msg = None
        source = None
        wait = WAITING
        max_retries = 3
        
        try:
            #Remove the filename from the url
            tmp = self.link.split("/file/")[1].split("/")[0]
            self.link = "%s/file/%s" % (BASE_URL, tmp)
            
            cookie = cookielib.CookieJar()
            opener = URLOpen(cookie) #cookielib
            
            with URLClose(opener.open(self.link)) as s:
                if self.wait_func():
                    return self.link, None, err_msg
                for line in s:
                    if 'check:' in line:
                        check = line.split("check:'")[1].replace("'","").strip()
                    elif "Recaptcha.create" in line:
                        tmp = line.split('("')[1].split('"')[0]
                        recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % tmp 
                        c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                        for retry in range(3):
                            if self.wait_func():
                                return self.link, None, err_msg
                            if retry < (max_retries + 1):
                                challenge, response = c.solve_captcha()
                                if response is not None:
                                    
                                    #Filefactory perfoms as check on its server by doing an
                                    #Ajax request sending the following data
                                    form = urllib.urlencode([("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response), ("recaptcha_shortencode_field", "undefined"),("check", check)])
                                    recaptcha_link = "%s/file/checkCaptcha.php" % BASE_URL

                                    #Getting the result back, status:{"ok"|"fail"}
                                    with URLClose(opener.open(recaptcha_link, form)) as sa:
                                        if self.wait_func():
                                            return self.link, None, err_msg
                                        for line in sa:
                                            if 'status:"ok"' in line:
                                                tmp = line.split('path:"')[-1].split('"')[0]
                                                tmp_link = "%s%s" %(BASE_URL, tmp)
                                                with URLClose(opener.open(tmp_link)) as sb:
                                                    if self.wait_func():
                                                        return self.link, None, err_msg
                                                    for line in sb:
                                                        if 'countdown">' in line:
                                                            #Try to get WAIT from the page
                                                            try:
                                                                tmp = line.split('countdown">')[-1].split("<")[0]
                                                                tmp = int(tmp)
                                                                if tmp > 320:
                                                                    raise LimitExceededException("Limit Exceeded")
                                                            except ValueError:
                                                                pass
                                                            else:
                                                                if tmp > 0:
                                                                    wait = tmp
                                                        if 'id="downloadLinkTarget' in line:
                                                            link_file = line.split('<a href="')[1].split('"')[0]
                                                            if self.wait_func(wait):
                                                                return self.link, None, err_msg
                                                            with URLClose(opener.open(link_file, range=(self.content_range, None)), always_close=False) as sc:
                                                                try:
                                                                    if sc.status == 302: #redirect error 302.
                                                                        raise RedirectException("Redirection error")
                                                                except AttributeError as err: #no redirected.
                                                                    source = sc
                                                            raise FileLinkFoundException()
                                else:
                                    raise CaptchaException("No response from the user")
                            else:
                                raise CaptchaException("Captcha, max retries reached")
                        raise LinkNotFoundException()
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except (RedirectException, FileLinkFoundException, LinkNotFoundException, CaptchaException, LimitExceededException) as err:
            if isinstance(err, LimitExceededException):
                self.set_limit_exceeded(True)
            elif not isinstance(err, FileLinkFoundException):
                logger.info(err)
                err_msg = err
        except Exception as err:
            logger.exception(err)
        
        return self.link, source, err_msg #puede ser el objeto archivo o None.

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)

