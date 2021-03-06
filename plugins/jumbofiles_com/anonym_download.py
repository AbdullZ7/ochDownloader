#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase

BASE_URL = "http://jumbofiles.com"


class PluginDownload(PluginBase):
    def parse(self):
        link = self.link
        file_id = self.link.split('jumbofiles.com/')[-1].split('/')[0]
        form = [("op", "download3"), ('id', file_id), ('rand', '')]
        page = self.get_page(link, form=form)
        self.source = self.click('METHOD="LINK" ACTION="(?P<link>[^"]+)', page, False)

        #m = self.get_match('name="rand" value="(?P<rand>[^"]+)', page)
        #if m is not None:
            #rand = m.group('rand')
            #file_id = self.link.split('jumbofiles.com/')[-1].split('/')[0]
            #form = [("op", "download2"), ('id', file_id), ('rand', rand),
            #        ('referer', ''), ('method_free', ''), ('method_premium', '')]
            #page = self.get_page(link, form=form)
        #else: #something changed
           # pass


if __name__ == "__main__":
    pass
