import importlib
import logging

from core import cons

logger = logging.getLogger(__name__)


def worker(plugin, username, password):
    try:
        module = importlib.import_module("plugins.{module}.account".format(module=plugin))
        account = module.PluginAccount(username, password)
        account.parse()
    except Exception as err:
        logger.exception(err)
        return cons.ACCOUNT_ERROR
    else:
        return account.status