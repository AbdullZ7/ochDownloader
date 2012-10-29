import importlib
import logging
logger = logging.getLogger(__name__)

#Libs
import cons
from idle_queue import idle_add_and_wait
from host_accounts import host_accounts


class PluginBridge:
    """"""
    def __init__(self, link, host, video_quality, content_range, wait_func):
        """"""
        self.link = link
        self.host = host
        self.video_quality = video_quality
        self.content_range = content_range
        self.wait_func = wait_func
        #
        self.dl_link = None
        self.cookie = None
        self.source = None
        self.err_msg = None
        self.premium = False
        self.limit_exceeded = False
        self.f_name = None

    def plugin_download(self):
        account_item = host_accounts.get_account(self.host)
        if account_item is not None:
            plugin_download = "premium_download"
            self.premium = True
        else:
            plugin_download = "anonym_download"
        logger.info(plugin_download)
        self.set_data(plugin_download, account_item)

    def set_data(self, plugin_download, account_item):
        try:
            module = importlib.import_module("plugins.{0}.{1}".format(self.host, plugin_download))
            p = module.PluginDownload(self.link, self.content_range, self.wait_func, account_item, self.video_quality)
            p.parse()
            self.source = p.source
            self.dl_link = p.dl_link
            self.cookie = p.cookie
            self.err_msg = p.err_msg
            self.limit_exceeded = p.limit_exceeded
            self.f_name = p.f_name
            self.video_quality = p.video_quality
            if not self.source and account_item is not None:
                account_status = p.get_account_status()
                self.disable_account(account_item, account_status)
        except Exception as err:
            self.err_msg = err
            logger.exception(err)

    def disable_account(self, account_item, account_status):
        if account_status in (cons.ACCOUNT_FAIL, cons.ACCOUNT_FREE): #login fail or free account.
            idle_add_and_wait(host_accounts.enable_account, account_item.host, account_item.id_account, False, True)