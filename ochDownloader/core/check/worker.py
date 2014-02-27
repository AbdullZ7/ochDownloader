import importlib
import logging

from core import const
from core import utils

logger = logging.getLogger(__name__)


def worker(plugin, url):
    if not plugin:
        return const.LINK_ERROR, None, 0, None

    try:
        module = importlib.import_module("plugins.{module}.checker".format(module=plugin))
        checker = module.Checker(url)
        checker.parse()
    except Exception as err:
        logger.exception(err)
        return const.LINK_ERROR, None, 0, str(err)
    else:
        name = utils.normalize_file_name(checker.name)
        return checker.status, name, checker.size, checker.message