#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore, LimitExceededError


BASE_URL = "http://uploaded.to"
WAITING = 20


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        link = self.link
        file_id = self.get_file_id()
        form_url = BASE_URL + "/io/ticket/slot/" + file_id
        page = self.get_page(form_url, form={})
        #
        m = self.get_match('(succ:true)', page, "Link not found")
        page = self.get_page(link)
        #
        self.countdown('period: <span>(?P<count>[^<]+)</span>', page, 320, WAITING)
        js_url = BASE_URL + "/js/download.js"
        page = self.get_page(js_url)
        #
        c_pattern = 'Recaptcha\.create\(.*?"(?P<key>[^"]+)'
        self.recaptcha_post_link = BASE_URL + "/io/ticket/captcha/" + file_id
        page = self.recaptcha(c_pattern, page)
        #
        #resume fix
        self.content_range = None
        self.source = self.click('url:\'(?P<link>[^\']+)', page, False)

    def recaptcha_success(self, pattern, page):
        #overriden
        if "Sie haben die max." in page:
            raise LimitExceededError("Limit Exceeded")
        elif "download" in page:
            return True
        else: #{err:"captcha"}
            return False

    def get_file_id(self):
        if "/ul.to/" in self.link:
            file_id = self.link.split("/ul.to/")[-1].split("/")[0]
        else:
            file_id = self.link.split("/file/")[-1].split("/")[0]
        return file_id