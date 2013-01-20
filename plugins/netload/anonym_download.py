#python libs
import re
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore, LimitExceededError
from addons.tesseract import tesseract, clean_image

BASE_URL = "http://netload.in"
WAITING = 30


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def parse(self):
        if "file_id" in self.link: #most likely not.
            file_id = self.link.split("file_id=")[-1].split("&")[0]
        else:
            file_id = self.link.split("netload.in/datei")[-1].split("/")[0].split(".")[0]
        link = self.link
        page = self.get_page(link)
        #
        m_pattern = 'Free_dl"><a href="(?P<link>[^"]+)'
        m = self.get_match(m_pattern, page, "Download not found")
        link = BASE_URL + "/" + m.group('link').replace("&amp;", "&")
        page = self.get_page(link)
        cn_pattern = '>countdown\((?P<count>[^,]+)'
        self.countdown(cn_pattern, page, 600, 30)
        #this pattern may not work
        #
        m_pattern = 'src="(?P<link>[^"]+)"[^"]+"Sicherheitsbild' #captcha
        m = self.get_match(m_pattern, page, "Captcha not found")
        link = BASE_URL + "/" + m.group('link')
        captcha_result = tesseract.get_solved_captcha(link, self.cookie, self.filter)
        #file_id = self.get_match()
        form = [("file_id", file_id), ("captcha_check", captcha_result), ("start", "")]
        captcha_form_url = BASE_URL + "/" + "index.php?id=10"
        page = self.get_page(captcha_form_url, form=form)
        self.countdown(cn_pattern, page, 600, 30)
        s_pattern = 'class="Orange_Link" href="(?P<link>[^"]+)'
        self.source = self.click(s_pattern, page, False)
    
    def countdown(self, pattern, page, limit, default):
        m = self.get_match(pattern, page, raise_err=False)
        if m is not None:
            wait = int(m.group('count')) / 100 #ms
            if wait >= limit:
                raise LimitExceededError("Limit Exceeded")
            else:
                self.wait_func(wait)
        else:
            self.wait_func(default)
    
    def filter(self, image):
        """"""
        image_ = clean_image.convert_to_greyscale(image)
        image_ = clean_image.clean_noise(image_, 3)
        return image_