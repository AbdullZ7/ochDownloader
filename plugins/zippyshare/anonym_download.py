#python libs
import urllib
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore
from addons.swfdump import dump


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        www = self.link.split('.')[0].split('/')[-1]
        link = 'http://%s.zippyshare.com/' % www
        page = self.get_page(self.link)
        time = self.get_time(link, page)
        key = self.link.split('/v/')[-1].split('/')[0] #file id
        data = [('key', key), ('time', time)]
        link += 'download?' + urllib.urlencode(data) #http://wwwXX.zippyshare.com/download?key=XXXX&time=XXXX
        self.source = self.get_page(link, close=False)

    def get_time(self, link, page):
        m = self.get_match('seed: (?P<seed>\d+)', page)
        m2 = self.get_match('embedSWF\("/(?P<swf>[^"]+)', page)
        link += m2.group('swf')
        swf_content = self.get_page(link) #may be None
        raw_swf = dump.get_swf_dump(swf_content) #may be None
        multiply, modulo = self.get_multiply_and_modulo(raw_swf) #may be None
        seed = m.group('seed')
        time = (int(seed) * multiply) % modulo
        return time

    def get_multiply_and_modulo(self, raw_swf):
        """
        00020) + 0:1 pushbyte 8
        ...
        00030) + 1:1 pushint 46784661
        """
        multiply = None
        modulo = None
        for line in raw_swf.splitlines():
            if 'pushbyte' in line:
                multiply = int(line.split('pushbyte')[-1].strip())
            elif 'pushint' in line:
                modulo = int(line.split('pushint')[-1].strip())
                break
        return multiply, modulo


if __name__ == "__main__":
    pass
