import threading
import logging

from core.plugin.config import services_dict

logger = logging.getLogger(__name__)

_uid = 0
_lock = threading.Lock()


def uid():
    global _uid, _lock

    with _lock:
        _uid += 1

    return str(_uid)


def get_host_from_url(url):
    i = 2 if url.startswith(("http://", "https://")) else 0
    host = url.split("/")[i]  # get (www.|subdomain.)website.com
    host_alt = ".".join(host.split(".")[1:])  # get (website.)com

    if host in services_dict:
        return host

    if host_alt in services_dict:
        return host_alt