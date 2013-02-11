import importlib
import logging
logger = logging.getLogger(__name__)

#Libs
from core import cons
from core.plugin.config import plugins_config
from core.dispatch.idle_queue import idle_add_and_wait
from base import ParsingError, StopParsing, LimitExceededError, CaptchaException

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

    def parse(self):
        conf = plugins_config.services_dict[self.host]
        if self.account_dict and (conf.get_premium_available() or conf.get_free_available()):
            self.check_account()
        if self.account_dict and self.account_dict['status'] == cons.ACCOUNT_PREMIUM:
            plugin_download = PREMIUM_MODULE
        elif self.account_dict and self.account_dict['status'] == cons.ACCOUNT_FREE:
            plugin_download = FREE_MODULE
        else:
            plugin_download = ANONYM_MODULE
        logger.info("%s %s" % (self.host, plugin_download))
        self.set_data(plugin_download)

    def set_data(self, plugin_download):
        try:
            module = importlib.import_module("plugins.{0}.{1}".format(self.host, plugin_download))
            p = module.PluginDownload(self.link, self.content_range, self.wait_func, self.cookie, self.video_quality)
            p.parse()
        except (ParsingError, LimitExceededError, CaptchaException) as err:
            if isinstance(err, LimitExceededError):
                self.limit_exceeded = True
                logger.warning("%s %s" % (self.host, str(err)))
            elif isinstance(err, CaptchaException):
                logger.warning("%s %s" % (self.host, str(err)))
            else: #ParsingError
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
        pass

