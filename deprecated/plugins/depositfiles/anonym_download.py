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


BASE_URL = "http://depositfiles.com"
WAITING = 60


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
        """"""
        link_file = None
        err_msg = None
        source = None
        wait = WAITING
        
        try:
            file_id = self.link.split("/files/")[1].split("/")[0]
            self.link = BASE_URL + "/files/" + file_id

            cookie = cookielib.CookieJar()
            opener = URLOpen(cookie) #cookielib
            
            form = urllib.urlencode([("gateway_result", "1"), ])
            
            with URLClose(opener.open(self.link)) as s1:
                if self.wait_func():
                    return self.link, None, err_msg
                s1.read()
                with URLClose(opener.open(self.link, form)) as s2:
                    for line in s2:
                        if 'download_waiter_remain">' in line:
                            wait = int(line.split('download_waiter_remain">')[-1].split('<')[0])
                        elif "Recaptcha.create('" in line:
                            key = line.split("Recaptcha.create('")[-1].split("'")[0]
                        elif "var fid" in line:
                            fid = line.split("'")[1]
                        elif 'limit_interval">' in line:
                            wait = int(line.split('limit_interval">')[-1].split("<")[0])
                            if wait > 320:
                                raise LimitExceededException("Limit Exceeded")
                        
                    if self.wait_func(wait):
                        return self.link, None, err_msg
                    if key is not None:
                        recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % key
                        c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                        for retry in range(3):
                            if self.wait_func(): #wait... if true: download was stopped
                                return self.link, None, err_msg
                            challenge, response = c.solve_captcha()
                            if response is not None:
                                recaptcha_url = BASE_URL + "/get_file.php?fid=" + fid + "&challenge=" + challenge + "&response=" + response
                                with URLClose(opener.open(recaptcha_url)) as s3:
                                    if self.wait_func():
                                        return self.link, None, err_msg
                                    for line in s3:
                                        if 'form action="' in line and not "recaptcha" in line:
                                            link_file = line.split('form action="')[-1].split('"')[0]
                                            #print link_file
                                            with URLClose(opener.open(link_file, range=(self.content_range, None)), always_close=False) as s4:
                                                source = s4
                                            raise FileLinkFoundException()
                                    err_msg = "Wrong captcha"
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


if __name__ == "__main__":
    pass