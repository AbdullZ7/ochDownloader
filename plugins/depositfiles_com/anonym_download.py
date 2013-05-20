#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from addons.captcha.recaptcha import PluginRecaptcha

BASE_URL = "http://depositfiles.com"
WAITING = 60


class PluginDownload(PluginRecaptcha):
    def parse(self):
        link = self.link
        form = [("gateway_result", "1"), ]
        page = self.get_page(link, form=form)
        m = self.get_match('var fid[^\']+\'(?P<fid>[^\']+)', page, "Captcha not found")
        self.fid = m.group('fid')
        cn_pattern = 'download_waiter_remain">(?P<count>[^<]+)'
        self.countdown(cn_pattern, page, 320, WAITING)
        c_pattern = 'Recaptcha\.create\(\'(?P<key>[^\']+)'
        page = self.recaptcha(c_pattern, page)
        s_pattern = 'form action="(?P<link>.*?)"'
        self.source = self.click(s_pattern, page, False)
    
    def recaptcha_post(self, pattern, page, challenge, response, *args, **kwargs):
        #overrided method
        self.recaptcha_post_link = BASE_URL + "/get_file.php?fid=" + self.fid + "&challenge=" + challenge + "&response=" + response
        page = self.get_page(self.recaptcha_post_link)
        return page


if __name__ == "__main__":
    pass
