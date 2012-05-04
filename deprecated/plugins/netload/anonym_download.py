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
from addons.tesseract import tesseract, clean_image

BASE_URL = "http://netload.in"
WAITING = 30


#custom exceptions
class FileLinkFoundException(Exception): pass
class LimitExceededException(Exception): pass
class LinkErrorException(Exception): pass
class CaptchaException(Exception): pass


class AnonymDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self):
        """
        TODO: Refactory.
        """
        link_file = None
        err_msg = None
        source = None
        wait = WAITING
        
        try:
            cookie = cookielib.CookieJar()
            opener = URLOpen(cookie) #cookielib
            
            #url parse
            if "file_id" in self.link: #most likely not.
                file_id = self.link.split("file_id=")[-1].split("&")[0]
            else:
                file_id = self.link.split("netload.in/datei")[-1].split("/")[0].split(".")[0]
            self.link = BASE_URL + "/" + "index.php?id=10&file_id=" + file_id
            
            with URLClose(opener.open(self.link)) as s1:
                if self.wait_func():
                    return self.link, None, err_msg
                for line in s1:
                    if 'class="Free_dl' in line:
                        id = line.split("?id=")[-1].split("&")[0]
                        url = BASE_URL + "/" + line.split('href="')[-1].split('"')[0].replace("&amp;", "&")
                        break
                with URLClose(opener.open(url)) as s2:
                    for line in s2:
                        if "captcha.php" in line:
                            captcha_url = BASE_URL + "/" + line.split('src="')[-1].split('"')[0]
                        elif ">countdown(" in line:
                            try:
                                wait = int(line.split(">countdown(")[-1].split(",")[0]) / 100 #ms
                            except Exception as err:
                                logger.exception(err)
                                wait = WAITING
                    if self.wait_func(wait+1):
                        return self.link, None, err_msg
                    captcha_result = tesseract.get_solved_captcha(captcha_url, cookie, self.filter)
                    form = urllib.urlencode([("file_id", file_id), ("captcha_check", captcha_result), ("start", "")])
                    captcha_form_url = BASE_URL + "/" + "index.php?id=" + id
                    with URLClose(opener.open(captcha_form_url, form)) as s3:
                        for line in s3:
                            if ">countdown(" in line:
                                try:
                                    wait = int(line.split(">countdown(")[-1].split(",")[0]) / 100 #ms
                                except Exception as err:
                                    logger.exception(err)
                                    wait = WAITING
                            elif 'class="Orange_Link' in line:
                                link_file = line.split('href="')[-1].split('"')[0]
                        if wait > 600: # 10 minutes
                            raise LimitExceededException("Limit exceeded")
                        if self.wait_func(wait+1):
                            return self.link, None, err_msg
                        with URLClose(opener.open(link_file, range=(self.content_range, None)), always_close=False) as s4:
                            source = s4
                        raise FileLinkFoundException()
            
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

    def filter(self, image):
        """"""
        image_ = clean_image.convert_to_greyscale(image)
        image_ = clean_image.clean_noise(image_, 3)
        return image_

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)










