#python libs
import json
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugin.base import PluginBase

BASE_URL = "http://multiupload.nl"


class PluginDownload(PluginBase):
    def parse(self):
        file_id = self.link.split("/")[-1]

        self.recaptcha_post_link = self.link + '?c=' + file_id

        page = self.get_page(self.link)
        c_pattern = 'Recaptcha\.create\("(?P<key>[^"]+)'
        page = self.recaptcha(c_pattern, page)
        json_response = json.loads(page)
        self.source = self.get_page(json_response['href'], close=False)

    def recaptcha_success(self, pattern, page):
        #overriden
        if 'href' in page:
            return True
        else:
            return False