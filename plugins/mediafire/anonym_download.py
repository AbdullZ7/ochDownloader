#python libs
import cookielib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore
#from addons.captcha.recaptcha import Recaptcha

BASE_URL = "http://mediafire.com"
COOKIE = cookielib.CookieJar()


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def parse(self):
        self.cookie = COOKIE
        self.link = self.link.replace("download.php", "")
        self.next_link = self.link
        c_pattern = 'http://www.google.com/recaptcha/api/challenge\?k=(?P<key>[^"]+)'
        page = self.recaptcha(c_pattern, self.get_page(self.link))
        file_id = self.link.split('?')[-1]
        s_pattern = '(?P<link>[^"]+/%s/[^"]+)' % file_id
        self.source = self.click(s_pattern, page, False)


if __name__ == "__main__":
    pass