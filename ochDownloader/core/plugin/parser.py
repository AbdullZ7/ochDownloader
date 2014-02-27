import importlib
import logging

from core import const
from core.plugin.config import services_dict
from core.plugin.exceptions import StopParsing, ParsingError, LimitExceededError

logger = logging.getLogger(__name__)

PREMIUM_MODULE = "premium_download"
FREE_MODULE = "free_download"
ANONYM_MODULE = "anonym_download"


class PluginParser:

    def __init__(self, downloader_item, wait_func):  # , account_dict):
        self.item = downloader_item
        self.wait_func = wait_func
        self.account_dict = None  # account_dict
        self.account_status = None

    def get_module_name(self):
        if self.account_dict:
            self.check_account()

        if self.account_status == const.ACCOUNT_PREMIUM:
            return PREMIUM_MODULE
        elif self.account_status == const.ACCOUNT_FREE:
            return FREE_MODULE
        else:
            return ANONYM_MODULE

    def parse(self):
        module_name = self.get_module_name()
        logger.debug("%s %s" % (self.item.host, module_name))

        try:
            path = "plugins.{plugin}.{module}".format(plugin=self.item.plugin,
                                                      module=module_name)
            module = importlib.import_module(path)
            p = module.PluginDownload(self.item, self.wait_func)
            p.parse()
        except ParsingError as err:
            self.item.message = str(err)
            logger.exception(err)
        except LimitExceededError as err:
            self.item.limit_exceeded = True
            self.item.message = str(err)
            logger.warning("%s %s" % (self.item.host, str(err)))
        except StopParsing as err:
            logger.debug("%s %s" % (self.item.host, str(err)))  # pass exc_info=True?
        except Exception as err:
            self.item.message = str(err)
            logger.exception(err)

    def check_account(self):
        # update account status
        # check if plugin supports premium or free and disable otherwise
        try:
            module = importlib.import_module("plugins.{plugin}.account".format(plugin=self.item.plugin))
            p = module.PluginAccount(self.account_dict['username'],
                                     self.account_dict['password'],
                                     self.item.cookie,
                                     self.wait_func)
            p.parse()
        except Exception as err:
            logger.exception(err)
        else:
            # disable if account is not free or premium or there is no plugin support
            try:
                conf = services_dict[self.item.host]
            except KeyError:
                return

            if (p.account_status == const.ACCOUNT_PREMIUM and conf.get_premium_available()) or \
                    (p.account_status == const.ACCOUNT_FREE and conf.get_free_available()):
                self.account_status = p.account_status
            else:
                self.disable_account()

    def disable_account(self):
        # TODO: make a signal... do not handle keyerror here
        # use a wrapper since the account may have been removed while we were here
        pass