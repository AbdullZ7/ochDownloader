import importlib
import logging
logger = logging.getLogger(__name__)

#Libs
from core import cons
from core.plugin.config import plugins_config
from core.accounts.manager import accounts_manager
from core.dispatch.idle_queue import idle_add_and_wait
from base import ParsingError, StopParsing, LimitExceededError

PREMIUM_MODULE = "premium_download"
FREE_MODULE = "free_download"
ANONYM_MODULE = "anonym_download"


class PluginParser:
    """"""
    def __init__(self, link, host, cookie, account_dict, video_quality, content_range, wait_func):
        """"""
        self.link = link
        self.host = host
        self.cookie = cookie
        self.account_dict = account_dict
        self.video_quality = video_quality
        self.content_range = content_range
        self.wait_func = wait_func

        self.dl_link = None
        self.cookie = None
        self.source = None
        self.err_msg = None
        self.limit_exceeded = False
        self.save_as = None

        self.account_status = None

    def parse(self):
        if self.account_dict:
            self.check_account()
        if self.account_status == cons.ACCOUNT_PREMIUM:
            module_name = PREMIUM_MODULE
        elif self.account_status == cons.ACCOUNT_FREE:
            module_name = FREE_MODULE
        else:
            module_name = ANONYM_MODULE
        logger.debug("%s %s" % (self.host, module_name))
        self.set_data(module_name)

    def set_data(self, module_name):
        try:
            module = importlib.import_module("plugins.{0}.{1}".format(self.host.replace('.', '_'), module_name))
            p = module.PluginDownload(self.link, self.host, self.content_range, self.wait_func, self.cookie, self.video_quality)
            p.parse()
        except (ParsingError, LimitExceededError) as err:
            if isinstance(err, LimitExceededError):
                self.limit_exceeded = True
                logger.warning("%s %s" % (self.host, str(err)))
            else:  # ParsingError
                logger.exception(err)
            if err:
                self.err_msg = str(err)
        except StopParsing as err:
            logger.debug("%s %s" % (self.host, str(err)))
        except Exception as err:
            self.err_msg = str(err)
            logger.exception(err)
        else:
            self.source = p.source
            self.dl_link = p.dl_link
            self.cookie = p.cookie
            self.save_as = p.save_as
            self.video_quality = p.video_quality

    def check_account(self):
        # update account status
        # check if plugin supports premium or free and disable otherwise
        try:
            module = importlib.import_module("plugins.{0}.account".format(self.host))
            p = module.PluginAccount(self.account_dict['username'], self.account_dict['password'], self.wait_func)
            p.parse()
        except Exception as err:
            logger.exception(err)
        else:
            # disable if account is not free or premium or there is no plugin support
            conf = plugins_config.services_dict[self.host]
            if (p.account_status == cons.ACCOUNT_PREMIUM and conf.get_premium_available()) or \
               (p.account_status == cons.ACCOUNT_FREE and conf.get_free_available()):
                self.cookie = p.cookie
                self.account_status = p.account_status
            else:
                self.disable_account()

    def disable_account(self):
        # use a wrapper since the account may have been removed while we were here
        def wrapper(host, id_account):
            try:
                accounts_manager.disable_account(host, id_account)
            except KeyError:
                pass
        idle_add_and_wait(wrapper, self.host, self.account_dict['id_account'])