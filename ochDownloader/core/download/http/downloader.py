import os
import time
import logging

from . import helpers
from .item import DownloaderItem
from .exceptions import DownloadError, DownloadStopped
from core import const
from core import utils
from core.config import conf
from core.plugin.parser import PluginParser
from core.accounts.manager import accounts_manager
from core.utils.concurrent.thread import Future

logger = logging.getLogger(__name__)


def spawn(item):
    di = DownloaderItem(item)
    fu = Future(target=start, args=(di, ))
    return fu, di.queue, di.stop_event

# TODO: rename file if exists and we are not resuming


def _start(di):
    create_path(di)

    di.file_exists = check_file_exists(di)
    if di.file_exists:
        di.content_range = get_content_range(di)

    plugin_parse(di)
    validate_source(di)
    di.name = get_filename(di)
    di.size = di.source.get_content_size()
    di.can_resume = di.source.can_resume()
    download(di)


def start(di):
    try:
        _start(di)
    except DownloadError as err:
        di.status = const.STATUS_ERROR
        di.message = "Error: {}".format(err)
        logger.warning(err)
    except DownloadStopped as err:
        di.status = const.STATUS_STOPPED
        di.message = _("Stopped")
        logger.debug(err)
    else:
        di.status = const.STATUS_FINISHED
        di.message = _("Completed")
    finally:
        if di.source:
            di.source.close()

        di.update()


def wait(di, seconds):
    """
    Non-blocking wait (thread-sleep).
    """
    while True:
        if not seconds or di.is_stopped():
            return

        time.sleep(1)
        seconds -= 1
        di.message = "{}: {}".format(_("Wait"), utils.time_format(seconds))
        di.update()


def check_file_exists(di):
    try:
        if di.name and os.path.isfile(os.path.join(di.path, di.name)):
            return True
        else:
            return False
    except OSError as err:
        logger.exception(err)
        raise DownloadError(err)


def create_path(di):
    try:
        if not os.path.exists(di.path):
            os.makedirs(di.path)
    except OSError as err:
        logger.exception(err)
        raise DownloadError(err)


def get_content_range(di):
    start_chunks = [start
                    for start, end in di.chunks
                    if start < end]
    return min(start_chunks, 0)


def plugin_parse(di):
    def wait_func(x):  # wrapper
        wait(di, seconds=x)

    pp = PluginParser(di, wait_func)
    pp.parse()

    if di.is_stopped():
        raise DownloadStopped("Stopped")

    if not di.source:
        raise DownloadError(di.message)


def get_filename(di):
    if di.save_as:
        return utils.normalize_file_name(di.save_as)
    else:
        return di.source.get_filename()


def validate_source(di):
    if not conf.get_html_dl() and di.source.is_html():
        raise DownloadError("HTML detected")


def download(di):
    if di.file_exists and di.chunks and helpers.is_valid_range(di.source, di.content_range, di.size):
        mode = "r+b"  # resume (with seek)
    else:
        mode = "wb"
        del di.chunks[:]

    try:
        # open file buffer only works on wb mode.
        # operations other than write will ignore it. (ex. seek)
        with open(os.path.join(di.path, di.name), mode) as fh:
            #pooler(fh)

            # make sure data is written to disk.
            fh.flush()
            os.fsync(fh.fileno())
    except OSError as err:
        logger.exception(err)
        raise DownloadError(err)