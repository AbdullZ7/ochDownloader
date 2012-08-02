#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore


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
        m = self.get_match('(succ:true)', page)
        if m is not None:
            page = self.get_page(link)
            self.countdown('period: <span>(?P<count>[^<]+)</span>', page, 320, WAITING)
            js_url = BASE_URL + "/js/download.js"
            page = self.get_page(js_url)
            c_pattern = 'Recaptcha\.create\(.*?"(?P<key>[^"]+)'
            self.next_link = BASE_URL + "/io/ticket/captcha/" + file_id
            page = self.recaptcha(c_pattern, page)
            #resume fix
            self.content_range = None
            self.source = self.click('url:\'(?P<link>[^\']+)', page, False)
        else: #link not found
            pass

    def recaptcha_post(self, pattern, page, challenge, response, extra_fields=None):
        #overrided method
        form_list = [("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response)]
        if extra_fields:
            form_list.extend(extra_fields)
        page = self.get_page(self.next_link, form_list, page)
        if "Sie haben die max." in page:
            self.err_msg = "Limit Exceeded"
            self.limit_exceeded = True
            return ("Limit Exceeded", page)
        elif "download" in page:
            return (None, page)
        else: #{err:"captcha"}
            return ("Wrong captcha", page)

    def get_file_id(self):
        if "/ul.to/" in self.link:
            file_id = self.link.split("/ul.to/")[-1].split("/")[0]
        else:
            file_id = self.link.split("/file/")[-1].split("/")[0]
        return file_id