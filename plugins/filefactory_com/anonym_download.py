#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from addons.captcha.recaptcha import PluginRecaptcha

#CONNECTION_RETRY = 3
BASE_URL = "http://www.filefactory.com"
WAITING = 60


class PluginDownload(PluginRecaptcha):
    def parse(self):
        link = self.link
        page = self.get_page(link)
        err_list = ('All free download slots are in use.', )
        self.validate(err_list, page)
        #
        m_pattern = 'check:[^\']+\'(?P<check>[^\']+)'
        m = self.get_match(m_pattern, page, "Captcha not found")
        c_pattern = 'Recaptcha\.create[^"]+"(?P<key>[^"]+)'
        extra_fields = [("check", m.group('check')), ]
        self.recaptcha_post_link = "%s/file/checkCaptcha.php" % BASE_URL
        page = self.recaptcha(c_pattern, page, extra_fields)
        #
        m_pattern = '"path":"(?P<path>.*?)"'
        m = self.get_match(m_pattern, page, "No path found")
        link2 = "%s%s" % (BASE_URL, m.group('path').replace("\\", ""))
        page = self.get_page(link2)
        #"all slots are taken" may appear here.
        cn_pattern = 'countdown">(?P<count>[^<]+)'
        self.countdown(cn_pattern, page, 320, WAITING)
        #
        file_id = self.link.split("/file/")[-1].split("/")[0]
        s_pattern = '<a href="(?P<link>[^"]+/%s/[^"]+)' % file_id
        #s_pattern = 'id="downloadLinkTarget[^<]+<a href="(?P<link>[^"]+)'
        self.source = self.click(s_pattern, page, False)

    def recaptcha_success(self, pattern, page):
        #overriden
        if '"status":"ok"' in page:
            return True
        else:
            return False


if __name__ == "__main__":
    import re
    page = """<p id="downloadLinkTarget" style="display: none;">
							"""
    pattern = 'id="downloadLinkTarget.*?<a href="(?P<link>.*?)"'
    m = re.search(pattern, page, re.S)
    if m is not None:
        print m.groups()
    else:
        print 'not found'