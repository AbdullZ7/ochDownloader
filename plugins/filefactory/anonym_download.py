#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore

#CONNECTION_RETRY = 3
BASE_URL = "http://www.filefactory.com"
WAITING = 60


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def parse(self):
        link = self.link
        page = self.get_page(link)
        err_list = ('All free download slots are in use.', )
        self.validate(err_list, page)
        m_pattern = 'check:[^\']+\'(?P<check>[^\']+)'
        m = self.get_match(m_pattern, page)
        if m is not None:
            c_pattern = 'Recaptcha\.create[^"]+"(?P<key>[^"]+)'
            extra_fields = [("check", m.group('check')), ]
            self.next_link = "%s/file/checkCaptcha.php" % BASE_URL
            page = self.recaptcha(c_pattern, page, extra_fields)
            #
            m_pattern = '"path":"(?P<path>.*?)"'
            m = self.get_match(m_pattern, page)
            if m is not None:
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
            else: #no path
                pass
        else: #captcha not found
            pass

    def recaptcha_post(self, pattern, page, challenge, response, extra_fields=None):
        #POST
        form_list = [("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response)]
        if extra_fields:
            form_list.extend(extra_fields)
        page = self.get_page(self.next_link, form_list, page)
        if '"status":"ok"' in page:
            return (None, page)
        else:
            return ("some error", page)


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