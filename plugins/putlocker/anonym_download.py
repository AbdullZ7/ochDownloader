#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore
from core import misc

BASE_URL = "http://www.putlocker.com"
WAITING = 10

class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        page = self.get_page(self.link)
        self.countdown('var countdownNum = (?P<count>[^;]+)', page, 320, WAITING)
        #value="da5444ca5740eab1" name="hash"
        m = self.get_match('value="(?P<hash>[^"]+)" name="hash"', page)
        if m is not None:
            form = [('hash', m.group('hash')), ('confirm', 'Continue as Free User')]
            page = self.get_page(self.link, form)
            s_pattern = 'href="(?P<link>/get_file.php[^"]+)'
            m = self.get_match(s_pattern, page)
            if m is not None:
                http_link = BASE_URL + m.group('link')
                self.source = self.get_page(http_link, close=False)
            else:
                self.err_msg = 'Link not found.'
        else:
            self.err_msg = 'Link not found.'


if __name__ == "__main__":
    pass
