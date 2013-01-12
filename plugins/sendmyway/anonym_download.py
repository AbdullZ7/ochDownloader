#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore

BASE_URL = "http://sendmyway.com"


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        page = self.get_page(self.link)
        file_id = self.link.split("/")[-1]
        m = self.get_match('name="rand" value="(?P<rand>[^"]+)', page)
        form = [("op", "download2"), ("id", file_id), ("rand", m.group('rand')),
                ("referer", ""), ("method_free", ""), ("method_premium", ""),
                ("down_script", "1")]
        page = self.get_page(self.link, form=form)
        s_pattern = 'href="(?P<link>[^"]+)" id="download_link'
        self.source = self.click(s_pattern, page, False)
