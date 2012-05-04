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


BASE_URL = "http://mediafire.com"


class FileLinkFoundException(Exception): pass
class PostCaptchaException(Exception): pass
class CaptchaException(Exception): pass
class LimitExceededException(Exception): pass
class LinkNotFoundException(Exception): pass


class AnonymDownload(PluginsCore):
    """
    TODO: fix redirect error to message 'ups, redirecting to your download'. Most likely do not download html files.
    """
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self):
        """"""
        try:
            link_file = None
            err_msg = None
            source = None
            cookie = cookielib.CookieJar()
            form = None
            max_retries = 3
            
            for retry in range(max_retries + 1):
                try:
                    file_id = self.link.split(".com/?")[-1].split("/")[0]
                    
                    with URLClose(URLOpen(cookie).open(self.link, form)) as s:
                        if self.wait_func():
                            return self.link, None, err_msg
                        s_lines = s.readlines()
                        for line in s_lines:
                            if 'class="download_link' in line:
                                div_list = line.split('<div')
                                tmp_list = [div for div in div_list if 'class="download_link' in div]
                                tmp_list = [ref_tag for ref_tag in tmp_list if file_id in ref_tag]
                                link_file = tmp_list[0].split('href="')[1].split('"')[0]
                            #Recaptcha
                            if "challenge?k=" in line:
                                if retry < (max_retries + 1):
                                    recaptcha_key = line.split("challenge?k=")[-1].split('"')[0]
                                    recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % recaptcha_key
                                    c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                                    challenge, response = c.solve_captcha()
                                    if response is not None:
                                        #Submit the input to the recaptcha system
                                        form = urllib.urlencode([("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response), ("downloadp", "")])
                                        raise PostCaptchaException("Post captcha solution")
                                    else:
                                        raise CaptchaException("No response from the user")
                                else:
                                    raise CaptchaException("Captcha, max retries reached")
                except PostCaptchaException as err:
                    pass
                else:
                    break
                
            if link_file is not None:
                with URLClose(URLOpen(cookie).open(link_file, range=(self.content_range, None)), always_close=False) as s:
                    source = s
                print link_file
            else:
                raise LinkNotFoundException("Link not found")
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            print err
            err_msg = err
        except (CaptchaException, LinkNotFoundException) as err:
            print err
            err_msg = err
            logging.exception(err)
        except Exception as err:
            err_msg = err
            print err
            logging.exception(err)
        
        return link_file, source, err_msg #puede ser el objeto archivo o None.

    def check_link(self, link):
            """"""
            return LinkChecker().check(link)

if __name__ == "__main__":

    def wait_func(some=None):
        return False
    def set_limit_exceeded():
        pass
    
    link = "http://www.mediafire.com/?9qdd57214q30cnu"
    content_range = None
    AnonymDownload(link, content_range, wait_func=wait_func, set_limit_exceeded=set_limit_exceeded).add()
    #print AnonymDownload(link, content_range, wait_func=wait_func, set_limit_exceeded=set_limit_exceeded).check_links(link)
    





