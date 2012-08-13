#python libs
import json
import urllib
import logging
logger = logging.getLogger(__name__)

#Libs
from core.plugins_core import PluginsCore

BASE_URL = "http://rapidgator.net"
WAITING = 0


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        page = self.get_page(self.link)

        err_list = ('Delay between downloads must be not less than', )
        self.validate(err_list, page)
        if self.err_msg and self.err_msg == err_list[0]:
            self.limit_exceeded = True
            return

        file_id = self.link.split("/file/")[-1].split("/")[0]
        ajax_link = BASE_URL + '/download/AjaxStartTimer'
        data = (('fid', file_id), )
        json_response = self.get_ajax(ajax_link, data=data)

        if json_response.get('state', '') == 'started':
            print "check 1"
            self.countdown('var secs = (?P<count>[^;]+)', page, 320, WAITING)

            ajax_link = BASE_URL + '/download/AjaxGetDownloadLink'
            data = (('sid', json_response['sid']), )
            json_response = self.get_ajax(ajax_link, data=data)

            if json_response.get('state', '') == 'done':
                print "check 2"
                link = BASE_URL + '/download/captcha'
                page = self.get_page(link)
                #TODO: continue

    def get_ajax(self, url, data):
        if data: url += '?' + urllib.urlencode(data)
        if self.is_running():
            try:
                response = self.get_page(url)
                return json.loads(response)
            except Exception as err:
                self.err_msg = err
        return {}


if __name__ == "__main__":
    pass
