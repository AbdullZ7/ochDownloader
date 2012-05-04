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
BASE_URL = "http://wupload.com"
WAITING = 20

class FileLinkFoundException(Exception): pass
class CaptchaException(Exception): pass
class LimitExceededException(Exception): pass
class LinkNotFoundException(Exception): pass


class AnonymDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self): #wait_func: wait method from thread_managed
        """
        http://api.wupload.com/
        """
        link_file = None
        err_msg = None
        source = None
        wait = WAITING
        found = False
        
        try:
            #Remove the filename from the url
            tmp = self.link.split("/file/")[1].split("/")[0]
            self.link = "%s/file/%s" % (BASE_URL, tmp)
            
            file_id = self.link.split("/")[-1].strip("/")
            cookie = cookielib.CookieJar()
            opener = URLOpen(cookie) #cookielib
            
            #form = urllib.urlencode([("checkTimeLimit", "check")]) #deprecated by fileserve
            if self.wait_func(): #wait... if true: download was stopped
                return self.link, None, err_msg
            
            """
            form_action = "{0}?start=1".format(link)
            it = opener.open(form_action)
            form_action = "{0}?start=1".format(it.geturl()) #get redirect url
            #end = form_action.split(".")[2].split("/")[0] #get .com replacement
            form_action2 = "{0}/{1}?start=1".format(link, file_id)
            #form_action2 = form_action2.replace(".com", end)
            form = urllib.urlencode([("foo", "foo")]) #force urllib2 to do a post
            headers = {"X-Requested-With": "XMLHttpRequest", }
            """
            
            it = opener.open(self.link)
            form_action = "{0}?start=1".format(it.geturl())
            form = urllib.urlencode({})
            headers = {"X-Requested-With": "XMLHttpRequest", }
            
            with URLClose(opener.open(form_action, form, headers=headers)) as s:
                if self.wait_func(): #wait... if true: download was stopped
                    return self.link, None, err_msg
                #when there is a countdown, the page need to be reloaded and search for the captcha again.
                for countdown in range(3):
                    for line in s:
                        if 'Recaptcha.create("' in line:
                            tmp = line.split('"')[1].split('"')[0]
                            recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % tmp
                            if self.wait_func(): #wait... if true: download was stopped
                                return self.link, None, err_msg
                            c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                            for retry in range(3):
                                challenge, response = c.solve_captcha()
                                if self.wait_func(): #wait... if true: download was stopped
                                    return self.link, None, err_msg
                                if response is not None:
                                    #Submit the input to the recaptcha system
                                    form = urllib.urlencode([("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response)])
                                    #recaptcha_url = "%s/checkReCaptcha.php" % BASE_URL
                                    
                                    with URLClose(opener.open(form_action, form)) as sa:
                                        for line in sa:
                                            if 'downloadLink' in line:
                                                sa.next()
                                                link_file = sa.next().split('href="')[-1].split('"')[0]
                                                with URLClose(opener.open(link_file, range=(self.content_range, None)), always_close=False) as sd:
                                                    source = sd #,content_range)
                                                raise FileLinkFoundException()
                                else:
                                    raise CaptchaException("No response from the user")
                                if retry == 2:
                                    raise CaptchaException("Captcha, max retries reached")
                        #Link already there O.o
                        elif 'downloadLink' in line:
                            s.next()
                            link_file = s.next().split('href="')[-1].split('"')[0]
                            with URLClose(opener.open(link_file, range=(self.content_range, None)), always_close=False) as sd:
                                source = sd #,content_range)
                            raise FileLinkFoundException()
                        #waiting... ?
                        elif "name='tm'" in line:
                            tm = line.split("value='")[-1].split("'")[0]
                            tm_hash = s.next().split("value='")[-1].split("'")[0]
                            form = urllib.urlencode([("tm", tm), ("tm_hash", tm_hash)])
                        #waiting...
                        elif "var countDownDelay" in line:
                            wait = int(line.split("=")[1].split(";")[0])
                            if wait < 60:
                                if self.wait_func(wait):
                                    return self.link, None, err_msg
                                s = opener.open(form_action, form) #fetch the page again. but posting the tm, tm_hash
                                break
                            else:
                                raise LimitExceededException("Limit Exceeded")
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except (FileLinkFoundException, CaptchaException, LimitExceededException, LinkNotFoundException) as err:
            if isinstance(err, LimitExceededException):
                self.set_limit_exceeded(True)
            elif not isinstance(err, FileLinkFoundException):
                logger.info(err)
                err_msg = err
        except Exception as err:
            logger.exception(err)
            err_msg = err
        
        return self.link, source, err_msg #puede ser el objeto archivo o None.
        

    def check_link(self, link):
            """"""
            return LinkChecker().check(link)