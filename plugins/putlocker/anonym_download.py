#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase, ParsingError, LimitExceededError

BASE_URL = "http://www.putlocker.com"
WAITING = 10


class PluginDownload(PluginBase):
    def parse(self):
        page = self.get_page(self.link)
        self.countdown('var countdownNum = (?P<count>[^;]+)', page, 320, WAITING)
        #value="da5444ca5740eab1" name="hash"
        m = self.get_match('value="(?P<hash>[^"]+)" name="hash"', page, "Link not found")
        form = [('hash', m.group('hash')), ('confirm', 'Continue as Free User')]
        page = self.get_page(self.link, form)
        s_pattern = 'href="(?P<link>/get_file.php[^"]+)'
        m = self.get_match_or_none(s_pattern, page)
        if m is not None:
            http_link = BASE_URL + m.group('link')
            self.source = self.get_page(http_link, close=False)
        elif self.get_match_or_none('exceeded the daily download limit', page) is not None:
            raise LimitExceededError("Limit Exceeded")
        else:
            raise ParsingError('Link not found.')


if __name__ == "__main__":
    pass
