#python libs
import cookielib
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase

BASE_URL = "http://mediafire.com"
COOKIE = cookielib.CookieJar()


class PluginDownload(PluginBase):
    def parse(self):
        self.cookie = COOKIE
        link = self.link.replace("download.php", "")
        self.recaptcha_post_link = link
        c_pattern = 'http://www.google.com/recaptcha/api/challenge\?k=(?P<key>[^"]+)'
        page = self.recaptcha(c_pattern, self.get_page(link))
        file_id = self.link.split('?')[-1]
        s_pattern = '(?P<link>[^"]+/%s/[^"]+)' % file_id
        self.source = self.click(s_pattern, page, False)


if __name__ == "__main__":
    pass