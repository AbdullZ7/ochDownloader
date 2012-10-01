#python libs
import urllib
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        page = self.get_page(self.link)
        time = self.get_time(page)
        if time:
            key = self.link.split('/v/')[-1].split('/')[0] #file id
            data = [('key', key), ('time', time)]
            www = self.link.split('.')[0].split('/')[-1]
            link = 'http://%s.zippyshare.com/download' % www
            link += '?' + urllib.urlencode(data) #http://wwwXX.zippyshare.com/download?key=XXXX&time=XXXX
            self.source = self.get_page(link, close=False)
        else:
            self.err_msg = "File not found."

    def get_time(self, page):
        m = self.get_match('seed: (?P<seed>\d+)', page)
        if m is not None:
            #these values were taken using "swfdump -a file.swf" from swftools
            multiply = 5 #pushbyte
            modulo = 71678963 #pushhint
            seed = m.group('seed')
            time = (int(seed) * multiply) % modulo
            return time
        return None


if __name__ == "__main__":
    pass
