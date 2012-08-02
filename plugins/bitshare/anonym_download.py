#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore

BASE_URL = "http://bitshare.com"
WAITING = 60


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def parse(self):
        link = self.link
        page = self.get_page(link)
        m_pattern = 'var ajaxdl[^"]+"(?P<ajaxid>[^"]+)'
        m = self.get_match(m_pattern, page)
        if m is not None:
            ajax_url = BASE_URL + "/files-ajax/" + m.group('ajaxid') + "/request.html"
            #
            form = [("request", "generateID"), ("ajaxid", m.group('ajaxid'))]
            page_ = self.get_page(ajax_url, form=form)
            self.countdown('file:(?P<count>.*?):', page_, 120, WAITING)
            #
            #this can be skipped
            c_pattern = 'challenge\?k=(?P<key>[^"]+)'
            extra_fields = [("request", "validateCaptcha"), ("ajaxid", m.group('ajaxid'))]
            self.next_link = ajax_url
            page_ = self.recaptcha(c_pattern, page, extra_fields)
            #
            form = [("request", "getDownloadURL"), ("ajaxid", m.group('ajaxid'))]
            page = self.get_page(ajax_url, form=form)
            s_pattern = 'SUCCESS#(?P<link>.*?)$'
            self.source = self.click(s_pattern, page, False)
        else: #link not found.
            pass


if __name__ == "__main__":
    import re
    page = 'SUCCESS#http://s45.bitshare.com/download.php?d=95708257284fa1714e6e399&g=0'
    pattern = 'SUCCESS#(?P<link>.*?)$'
    m = re.search(pattern, page, re.S)
    if m is not None:
        print m.groups()
    else:
        print 'not found'


