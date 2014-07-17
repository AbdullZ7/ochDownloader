import os
import re
import subprocess
import html.entities
import logging
from http import cookiejar
from urllib.parse import unquote_plus

from core import const

logger = logging.getLogger(__name__)


def subprocess_call(*args, **kwargs):
    if const.OS_WIN:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = startupinfo

    retcode = subprocess.call(*args, **kwargs)
    return retcode


def subprocess_popen(*args, **kwargs):
    if const.OS_WIN:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = startupinfo

    popen = subprocess.Popen(*args, **kwargs)
    return popen


def open_folder_window(path):
    try:
        if const.OS_WIN:
            os.startfile(os.path.normpath(path), "explore")
            # subprocess("explorer") is buggy, the explorer process never dies.
        elif const.OS_UNIX:
            subprocess_popen(["xdg-open", path], shell=True)
        else:  # mac
            subprocess_popen(["open", path], shell=True)
    except OSError as err:
        logger.warning(err)


def run_file(path):
    try:
        if const.OS_WIN:
            subprocess_popen([path, ], shell=True)
    except OSError as err:
        logger.warning(err)


def links_parser(text):
    return [link
            for line in text.splitlines()
            for link in line.split(" ")
            if link.startswith(("http://", "https://"))]


def smart_str(s, encoding='utf-8', errors='strict'):
    # TODO: remove, this is useless in python 3
    if isinstance(s, str):
        return s

    try:
        if isinstance(s, bytes):
            return str(s, encoding, errors)
        else:
            return str(s)
    except UnicodeDecodeError as err:
        logger.exception(err)
        raise


def time_format(s):
    m, s = divmod(int(s), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d:
        return "{:.0f}d {:.0f}h {:.0f}m".format(d, h, m)
    elif h:
        return "{:.0f}h {:.0f}m {:.0f}s".format(h, m, s)
    elif m:
        return "{:.0f}m {:.0f}s".format(m, s)
    else:
        return "{:.0f}s".format(s)


def size_format(b):
    kb, b = divmod(b, 1024)
    mb, kb = divmod(kb, 1024)
    gb, mb = divmod(mb, 1024)

    if gb:
        return "{:.2f}GB".format(gb + (mb / 1024))
    elif mb:
        return "{:.0f}MB".format(mb)
    elif kb:
        return "{:.0f}KB".format(kb)
    else:
        return "{:.0f}Bytes".format(b)


def speed_format(b):
    return size_format(b) + "/s"


def get_filename_from_url(url):
    return os.path.split(url)[-1].split("?")[0]


def strip(input, to_strip=None):
    # @to_strip: a string/list of chars you want to strip
    for x in to_strip or []:
        input = input.replace(x, '')

    return input


def normalize_file_name(name):
    name = html_entities_parser(name)
    name = unquote_plus(name)
    name = strip(name, to_strip='/\\:*?"<>|')
    name = name.strip('.')
    return name.strip()


def tail(fh, lines_limit=20):
    """
    Read file from bottom to top (on reverse)
    @fh: file opened in binary mode
    """
    BUFSIZ = 1024
    fh.seek(0, 2)
    bytes = fh.tell()
    size = lines_limit
    block = -1
    data = []

    while size > 0 and bytes > 0:
        if (bytes - BUFSIZ) > 0:
            # Seek back one whole BUFSIZ
            fh.seek(block*BUFSIZ, 2)
            # read BUFFER
            data.append(fh.read(BUFSIZ))
        else:
            # file too small, start from begining
            fh.seek(0, 0)
            # only read what was not read
            data.append(fh.read(bytes))

        lines_found = len(data[-1].splitlines())
        size -= lines_found
        bytes -= BUFSIZ
        block -= 1

    data.reverse()
    return b'\n'.join(b''.join(data).splitlines()[-lines_limit:])


def html_entities_parser(text):
    """
    Replace HTML or XML character references and entities from a text string.
    return The plain text, as a Unicode string, if necessary.
    """
    def fixup(m):
        text = m.group(0)

        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                else:
                    return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = html.entities.html5[text[1:]]
            except KeyError:
                pass

        return text  # leave as is

    return re.sub("&#?\w+;", fixup, text)


def url_unescape(url):
    entities = {
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": "\"",
        # must do ampersand last
        "&amp;": "&",
    }

    for k, v in entities.items():
        url = url.replace(k, v)

    return url


def load_cookie(path):
    cj = cookiejar.MozillaCookieJar()
    cj.magic_re = ''  # fixes LoadError, netscape header comment checking.

    try:
        cj.load(path)
    except Exception as err:
        logger.warning(err)
        return
    else:
        return cj


def remove_file(path):
    try:
        os.remove(path)
    except OSError as err:
        logger.exception(err)