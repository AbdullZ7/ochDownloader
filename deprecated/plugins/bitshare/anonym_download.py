#python libs
import urllib, urllib2, httplib, socket
import json
import cookielib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from link_checker import LinkChecker
from core.plugins_core import PluginsCore
from core.network.connection import URLOpen, URLClose #leer/abrir urls. And close connection if except raises.
from addons.captcha.recaptcha import Recaptcha


BASE_URL = "http://bitshare.com"
WAITING = 60


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
        wait = WAITING
        ajax_id = None
        recaptcha_key = None
        
        try:
            file_id = self.link.split("/files/")[1].split("/")[0]

            cookie = cookielib.CookieJar()
            opener = URLOpen(cookie) #cookielib
            ajax_id_url = BASE_URL + "/files-ajax/" + file_id + "/request.html"
            
            with URLClose(opener.open(self.link)) as s1:
                for line in s1:
                    if "var ajaxdl" in line:
                        ajax_id = line.split('"')[1]
                    elif "challenge?k=" in line:
                        recaptcha_key = line.split("challenge?k=")[-1].split('"')[0].strip()
                if not ajax_id: #not recaptcha_key or not ajax_id:
                    raise LinkErrorException("Link not found.")
                
                if self.wait_func():
                    return self.link, None, err_msg
                
                #wait time.
                #note: bitshare does not care for this. It can be skipped.
                #headers = {"Accept:": "application/json", }
                form = urllib.urlencode([("request", "generateID"), ("ajaxid", ajax_id)])
                with URLClose(opener.open(ajax_id_url, form)) as s2:
                    response = s2.read() #may return ERROR: explanation
                    wait = int(response.split(":")[1]) #file:60:1
                    if wait > 120:
                        raise LimitExceededException("Limit Exceeded")
                    if self.wait_func(wait):
                        return self.link, None, err_msg
                
                #recaptcha.
                #note: bitshare does not care for this. It can be skipped.
                if recaptcha_key:
                    recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % recaptcha_key
                    for retry in range(3):
                        c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                        challenge, response = c.solve_captcha()
                        if response is not None:
                            form = urllib.urlencode([("request", "validateCaptcha"), ("ajaxid", ajax_id), ("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response)])
                            response_ = opener.open(ajax_id_url, form).read() #may return ERROR: explanation or SUCCESS
                            if not "ERROR" in response_:
                                break
                        else:
                            raise CaptchaException("No response from the user")
                    if "ERROR" in response_:
                        raise CaptchaException("Wrong captcha")
                
                if self.wait_func():
                    return self.link, None, err_msg
                
                #get download link
                form = urllib.urlencode([("request", "getDownloadURL"), ("ajaxid", ajax_id)])
                with URLClose(opener.open(ajax_id_url, form)) as s3:
                    response = s3.read()
                    link_file = response.split("http")[-1]
                    link_file  = "http" + link_file
                
                with URLClose(URLOpen(cookie).open(link_file, range=(self.content_range, None)), always_close=False) as sc:
                    source = sc
                
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except (LimitExceededException, CaptchaException, LinkErrorException) as err:
            if isinstance(err, LimitExceededException):
                self.set_limit_exceeded(True)
            err_msg = err
            logger.info(err)
        except Exception as err:
            err_msg
            logger.exception(err)
            
        return link_file, source, err_msg

def check_link(self, link):
        """"""
        return LinkChecker().check(link)


if __name__ == "__main__":
    pass




    
