#python libs
import logging
logger = logging.getLogger(__name__)

#Libs
from core import cons
from core.plugin.account import PluginAccountBase

BASE_URL = "http://4shared.com"


class PluginAccount(PluginAccountBase):
    def parse(self):
        page = self.get_page(BASE_URL)
        form = (('login', self.username), ('password', self.password), ('remember', 'true'))
        url = 'https://www.4shared.com/'
        page = self.get_page(url, form) # https returns a blank source code
        cookie_dict = self.get_cookie_as_dict()
        if cookie_dict.get('Login', None) is not None:
            self.account_status = cons.ACCOUNT_FREE # or PREMIUM, who knows
        else:
            self.account_status = cons.ACCOUNT_ERROR

if __name__ == "__main__":
    user = 'john@doe.com'
    pw = 'password'
    plugin = PluginAccount(user, pw)
    plugin.parse()
    print plugin.account_status