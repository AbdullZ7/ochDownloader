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

BASE_URL = "http://fileserve.com"


#custom exceptions
class LimitExceededException(Exception): pass
class LinkErrorException(Exception): pass
class CaptchaException(Exception): pass


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
        wait = None
        found = False
        
        try:
            #Remove the filename from the url
            tmp = self.link.split("/file/")[1].split("/")[0]
            self.link = "%s/file/%s" % (BASE_URL, tmp)
            
            file_id = self.link.split("/")[-1].strip("/")
            cookie = cookielib.CookieJar()
            opener = URLOpen(cookie) #cookielib
            
            #form = urllib.urlencode([("checkTimeLimit", "check")]) #deprecated by fileserve
            form = urllib.urlencode([("checkDownload", "check")])
            post_result = opener.open(self.link, form).read()
            if "success" not in post_result:
                if "timeLimit" in post_result:
                    raise LimitExceededException("Limit Exceeded")
                else:
                    raise LinkErrorException("Link Error")
            
            with URLClose(opener.open(self.link)) as s:
                for line in s:
                    if 'reCAPTCHA_publickey=' in line:
                        tmp = line.split("'")[1].split("'")[0]
                        recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % tmp
                        if self.wait_func(): #wait... if true: download was stopped
                            return self.link, None, err_msg
                        c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                        for retry in range(3):
                            if self.wait_func(): #wait... if true: download was stopped
                                return self.link, None, err_msg
                            challenge, response = c.solve_captcha()
                            if response is not None:
                                #Submit the input to the recaptcha system
                                form = urllib.urlencode([("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response), ("recaptcha_shortencode_field", file_id)])
                                recaptcha_url = "%s/checkReCaptcha.php" % BASE_URL
                                
                                #Captcha is good
                                #on error: {"success":0,"error":"incorrect-captcha-sol"}
                                #on succes: {"success":1}
                                with URLClose(opener.open(recaptcha_url, form)) as sa:
                                    if "error" not in sa.read():
                                        form = urllib.urlencode([("downloadLink", "wait")])
                                        with URLClose(opener.open(self.link, form)) as sb:
                                            wait = int(sb.read()[-2:]) #somethimes gives fail404
                                            if self.wait_func(wait): #wait... if true: download was stopped
                                                return self.link, None, err_msg
                                            form = urllib.urlencode([("downloadLink", "show")])
                                            with URLClose(opener.open(self.link, form)) as sc:
                                                if self.wait_func(): #wait... if true: download was stopped
                                                    return self.link, None, err_msg
                                                sc.read()
                                                form = urllib.urlencode([("download", "normal")])
                                                with URLClose(opener.open(self.link, form, range=(self.content_range, None)), always_close=False) as sd:
                                                    if sd.url == self.link: #link not found or weird countdown issue
                                                        #logger.debug(sd.read())
                                                        raise LinkErrorException("Link Error, redirected")
                                                    else:
                                                        source = sd #,content_range)
                                            break
                                    else:
                                        err_msg = "Wrong captcha"
                            else:
                                raise CaptchaException("No response from the user")
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except (LimitExceededException, LinkErrorException, CaptchaException) as err:
            if isinstance(err, LimitExceededException):
                self.set_limit_exceeded(True)
            err_msg = err
            logger.info(err)
        except Exception as err:
            logger.exception(err)
            err_msg = err
        
        return self.link, source, err_msg #puede ser el objeto archivo o None.

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)

    
