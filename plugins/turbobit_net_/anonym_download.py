#python libs
import urllib, urllib2, httplib, socket
import cookielib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from link_checker import LinkChecker
from core.plugin.base import PluginBase
from core.network.connection import URLOpen, URLClose #leer/abrir urls. And close connection if except raises.
from addons.captcha.recaptcha import Recaptcha


BASE_URL = "http://turbobit.net"
WAITING = 60


#custom exceptions
class FileLinkFoundException(Exception): pass
class LimitExceededException(Exception): pass
class LinkErrorException(Exception): pass
class CaptchaException(Exception): pass


class AnonymDownload(PluginBase):
    """"""
    def __init__(self, *args, **kwargs):
        PluginBase.__init__(self, *args, **kwargs)
    
    def add(self): #wait_func: wait method from thread_managed
        """
        TODO: Refactory.
        """
        link_file = None
        err_msg = None
        source = None
        wait = WAITING
        
        try:
            file_id = self.link.split("turbobit.net/")[-1].split("/")[0].rstrip(".html")
            self.link = BASE_URL + "/download/free/" + file_id
            cookie = cookielib.CookieJar()
            opener = URLOpen(cookie) #cookielib
            
            with URLClose(opener.open(self.link)) as s1:
                key = None
                for line in s1:
                    if "challenge?k=" in line:
                        key = line.split('challenge?k=')[-1].split('"')[0]
                        recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % key
                        c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                        break
                if key is None:
                    raise LimitExceededException("Limit Exceeded")
                for retry in range(3):
                    challenge, response = c.solve_captcha()
                    if response is not None:
                        form = urllib.urlencode([("recaptcha_challenge_field", challenge),
                                                            ("recaptcha_response_field", response),
                                                            ("captcha_type", "recaptcha"),
                                                            ("captcha_subtype", "")])
                        with URLClose(opener.open(self.link, form)) as s2:
                            found = False
                            for line in s2:
                                if "limit :" in line:
                                    found = True
                                    try:
                                        wait = int(line.split(":")[-1].split(",")[0]) / 100 #ms
                                    except Exception as err:
                                        logger.exception(err)
                                        wait = WAITING
                                elif "captcha-error" in line:
                                    err_msg = "Wrong captcha"
                            if found:
                                if self.wait_func(wait+1):
                                    return self.link, None, err_msg
                                url = BASE_URL + "/download/getLinkAfterTimeout/" + file_id
                                print url
                                with URLClose(opener.open(url)) as s3:
                                    for line in s3:
                                        print line
                                        if "href='/download/redirect" in line:
                                            tmp = line.split("href='")[-1].split("'")[0]
                                            redir_url = BASE_URL + tmp
                                            print redir_url
                                            with URLClose(opener.open(redir_url)) as s4:
                                                for line in s4:
                                                    if 'href="' in line:
                                                        link_file = line.split('href="')[-1].split('"')[0]
                                                        #print link_file
                                                        with URLClose(opener.open(link_file, range=(self.content_range, None)), always_close=False) as s5:
                                                            source = s5
                                                        raise FileLinkFoundException()
                    else:
                        raise CaptchaException("No response from the user")

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











