#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore
#from addons.captcha.recaptcha import Recaptcha

BASE_URL = "http://mediafire.com"


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def parse(self):
        link = self.link
        c_pattern = 'http://www.google.com/recaptcha/api/challenge\?k=(?P<key>.*?)"'
        page = self.recaptcha(c_pattern, self.get_page(link))
        file_id = self.link.split('/?')[-1]
        s_pattern = '(?P<link>[^"]+/%s/[^"]+)' % file_id
        self.source = self.click(s_pattern, page, False)


if __name__ == "__main__":
    pass
    import re
    page = '"http://some" kNO = "http://205.196.123.44/27girlme3cxg/asdasdasdasd/some.rar";'
    pattern = '([^"]+/xupyqzhcsh3wqhy/[^"]+)'
    m = re.search(pattern, page, re.S)
    if m is not None:
        print m.groups()
    else:
        print 'not found'
    





