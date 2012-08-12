#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore

BASE_URL = "http://oron.com"
WAITING = 60


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def parse(self):
        link = self.link
        file_id = self.link.split("/oron.com/")[1].split("/")[0]
        page = self.get_page(link)
        m = self.get_match('name="fname".*?value="(?P<fname>.*?)"', page)
        if m is not None:
            dict_form = {"op": "download1", "usr_login": "", "id": file_id, "fname": m.group('fname'), "referer": "", "method_free": " Regular Download "}
            page = self.get_page(link, form=dict_form)
            self.countdown('id="countdown">(?P<count>.*?)<', page, 320, 60)
            #get_form





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
        
        try:
            #Remove the filename from the url
            file_id = self.link.split("/oron.com/")[1].split("/")[0]
            self.link = "%s/%s" % (BASE_URL, file_id)
            
            cookie = cookielib.CookieJar()
            
            with URLClose(URLOpen(cookie).open(self.link)) as s:
                if self.wait_func():
                    return self.link, None, err_msg
                fname = None
                for line in s:
                    if 'name="fname"' in line:
                        fname = line.split('value="')[-1].split('"')[0]
                if fname is not None:
                    dict_form = {"op": "download1", "usr_login": "", "id": file_id, "fname": fname, "referer": "", "method_free": " Regular Download "}
                    headers = {"Content-type": "application/x-www-form-urlencoded", }
                    with URLClose(URLOpen(cookie).open(self.link, urllib.urlencode(dict_form), headers=headers)) as sa:
                        if self.wait_func():
                            return self.link, None, err_msg
                        rand = None
                        referer = None
                        recaptcha_key = None
                        for line in sa:
                            if 'id="countdown"' in line:
                                wait = int(line.split('id="countdown">')[-1].split('<')[0].strip())
                            elif 'name="rand"' in line:
                                rand = line.split('value="')[-1].split('"')[0]
                            elif 'name="referer"' in line:
                                referer = line.split('value="')[-1].split('"')[0]
                            elif "challenge?k=" in line:
                                recaptcha_key = line.split("challenge?k=")[-1].split('"')[0]
                        if None not in (rand, referer, recaptcha_key):
                            if self.wait_func(wait): #wait... if true: download was stopped
                                return self.link, None, err_msg
                            
                            recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % recaptcha_key
                            c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                            challenge, response = c.solve_captcha()
                            if response is not None:
                                dict_form = {"op": "download2", "id": file_id, "rand": rand, "referer": referer,
                                                    "method_free": " Regular Download ", "method_premium": "",
                                                    "recaptcha_challenge_field": challenge, "recaptcha_response_field": response, "down_direct": "1"}
                                with URLClose(URLOpen(cookie).open(self.link, urllib.urlencode(dict_form), headers=headers)) as sb:
                                    if self.wait_func():
                                        return self.link, None, err_msg
                                    for line in sb:
                                        if 'class="atitle"' in line:
                                            link_file = line.split('href="')[-1].split('"')[0]
                                        elif "Wrong captcha" in line:
                                            raise CaptchaException("Wrong captcha")
                                    if link_file is not None:
                                        with URLClose(URLOpen(cookie).open(link_file, range=(self.content_range, None)), always_close=False) as sc:
                                            source = sc
                                    else: #link not found
                                        raise LinkErrorException("Link Error")
                            else:
                                raise CaptchaException("No response from the user")
                        else: #limit exceeded
                            #TODO: Fix for big files (+1gb), since regular users cant download them
                            raise LimitExceededException("Limit Exceeded")
                else: #link not found
                    raise LinkErrorException("Link Error")
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            err_msg = err
        except (LimitExceededException, CaptchaException, LinkErrorException) as err:
            if isinstance(err, LimitExceededException):
                self.set_limit_exceeded(True)
            err_msg = err
            logger.info(err)
        except Exception as err:
            err_msg = err
            logger.exception(err)
        
        return link_file, source, err_msg #puede ser el objeto archivo o None.

    def check_link(self, link):
        """"""
        return LinkChecker().check(link)
