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


BASE_URL = "http://uploaded.to"
WAITING = 20


#custom exceptions
class FileLinkFoundException(Exception): pass
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
        
        try:
            if "/ul.to/" in self.link:
                file_id = self.link.split("/ul.to/")[-1].split("/")[0]
            else:
                file_id = self.link.split("/file/")[-1].split("/")[0]
            self.link = BASE_URL + "/file/" + file_id

            cookie = cookielib.CookieJar()
            opener = URLOpen(cookie) #cookielib
            
            with URLClose(opener.open(self.link)) as s1:
                if self.wait_func():
                    return self.link, None, err_msg
                for line in s1:
                    if 'class="free' in line:
                        try:
                            s1.next()
                            wait = int(s1.next().split("<span>")[-1].split("</span>")[0])
                        except Exception as err:
                            logger.exception(err)
                            wait = WAITING
                        break
                form = urllib.urlencode({})
                form_url = BASE_URL + "/io/ticket/slot/" + file_id
                with URLClose(opener.open(form_url, form)) as s2:
                    s = s2.read()
                    if "succ:true" in s:
                        if self.wait_func(wait):
                            return self.link, None, err_msg
                        js_url = BASE_URL + "/js/download.js"
                        with URLClose(opener.open(js_url)) as s3:
                            if self.wait_func():
                                return self.link, None, err_msg
                            for line in s3:
                                if 'Recaptcha.create("' in line:
                                    key = line.split('Recaptcha.create("')[-1].split('"')[0].strip()
                                    break
                        print key
                        recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % key
                        c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                        for retry in range(3):
                            challenge, response = c.solve_captcha()
                            if response is not None:
                                form_url = BASE_URL + "/io/ticket/captcha/" + file_id
                                form = urllib.urlencode([("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response)])
                                with URLClose(opener.open(form_url, form)) as s4:
                                    if self.wait_func():
                                        return self.link, None, err_msg
                                    s = s4.read()
                                    if "download" in s:
                                        link_file = s.split("url:'")[-1].split("'")[0]
                                        print link_file
                                        with URLClose(opener.open(link_file, range=(self.content_range, None)), always_close=False) as s5:
                                            source = s5
                                        raise FileLinkFoundException()
                                    elif "limit-dl" in s:
                                        raise LimitExceededException("Limit Exceeded")
                                    else: #{err:"captcha"}
                                        print s
                                        err_msg = "Wrong captcha"
                            else:
                                raise CaptchaException("No response from the user")
                    else:
                        LinkErrorException("Link not found")
        
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except (FileLinkFoundException, LimitExceededException, LinkErrorException, CaptchaException) as err:
            if isinstance(err, LimitExceededException):
                self.set_limit_exceeded(True)
            err_msg = err
            logger.info(err)
        except Exception as err:
            logger.exception(err)
            err_msg = err
        
        return link_file, source, err_msg

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)





