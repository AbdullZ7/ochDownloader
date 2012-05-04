#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore
from addons.captcha.recaptcha import Recaptcha

BASE_URL = "http://mediafire.com"


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def parse(self):
        link = self.link
        c_pattern = 'http://www.google.com/recaptcha/api/challenge\?k=(?P<key>.*?)"'
        page = self.recaptcha(c_pattern, self.get_page(link))
        s_pattern ='class="download_link".*?href="(?P<link>.*?)"'
        self.source = self.click(s_pattern, page, False)


if __name__ == "__main__":
    def wait_func(some=None):
        return False
    
    pass
    





