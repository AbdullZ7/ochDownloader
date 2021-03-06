import os
import ctypes
import re
import htmlentitydefs
import subprocess
import urllib
import cookielib
import logging
logger = logging.getLogger(__name__)

import cons


def keep_system_awake(stop=False):
    """
    Prevent from going to sleeping state.
    TODO: implement.
    """
    #UNTESTED. check if the system go to sleep if the process is terminated
    mode_dict = {
        "ES_AWAYMODE_REQUIRED": "0x00000040",
        "ES_CONTINUOUS": "0x80000000",
        "ES_DISPLAY_REQUIRED": "0x00000002",
        "ES_SYSTEM_REQUIRED": "0x00000001",
        "ES_USER_PRESENT": "0x00000004"
    }
    try:
        if cons.OS_WIN:
            if not stop:
                ctypes.windll.kernel32.SetThreadExecutionState(mode_dict["ES_CONTINUOUS"] | mode_dict["ES_SYSTEM_REQUIRED"])
            else:
                ctypes.windll.kernel32.SetThreadExecutionState(mode_dict["ES_CONTINUOUS"]) #go to sleep if you wanna.
            #or test:
            #while True:
                #ctypes.windll.kernel32.SetThreadExecutionState(mode_dict["ES_SYSTEM_REQUIRED"]) #reset idle timer
                #time.sleep(50)
    except Exception as err:
        logger.exception(err)


def get_free_space(folder):
    """
    Return folder/drive free space in bytes.
    TODO: implement.
    """
    try:
        if cons.OS_WIN:
            free_bytes = ctypes.c_ulonglong(0)
            retcode = ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            if retcode == 0:
                raise OSError("Windows error on get free space")
            return free_bytes.value
        else:
            s = os.statvfs(folder)
            #return os.statvfs(folder).f_bfree
            return s.f_bsize * s.f_bavail
    except Exception as err:
        logger.exception(err)


def subprocess_call(*args, **kwargs):
    #hide console window on Windows. Python 2.7 only.
    if cons.OS_WIN:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess._subprocess.SW_HIDE
        kwargs['startupinfo'] = startupinfo
    retcode = subprocess.call(*args, **kwargs)
    return retcode


def subprocess_popen(*args, **kwargs):
    #hide console window on Windows. Python 2.7 only.
    if cons.OS_WIN:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess._subprocess.SW_HIDE
        kwargs['startupinfo'] = startupinfo
    popen = subprocess.Popen(*args, **kwargs)
    return popen


def open_folder_window(path):
    """"""
    try:
        if cons.OS_WIN:
            os.startfile(os.path.normpath(path), "explore")
            #subprocess_popen(["explorer", "/select,", os.path.join(path, file_name)], shell=True) #bug: the process never exits
        elif cons.OS_UNIX:
            subprocess_popen(["xdg-open", path], shell=True)
        else: #mac
            subprocess_popen(["open", path], shell=True)
    except OSError as err:
        logger.warning(err)


def run_file(path):
    """"""
    try:
        if cons.OS_WIN:
            subprocess_popen([path, ], shell=True)
    except OSError as err:
        logger.warning(err)


def links_parser(text):
    return [link
            for line in text.splitlines()
            for link in line.split(" ") if link.startswith(("http://", "https://"))]


def smart_unicode(s, encoding='utf-8', errors='strict'):
    if isinstance(s, unicode):
        return s
    elif not isinstance(s, basestring): #not a string
        return unicode(s)
    else:
        try:
            return unicode(s, encoding, errors)
        except UnicodeDecodeError:
            try:
                return unicode(s, 'latin-1', 'replace')
            except UnicodeDecodeError as err:
                logger.exception(err)
                return s


def time_format(the_time):
    """
    BUG: seconds go from 1 to 60, etc... dont remember. Should be from 0 to 59...
    """
    m, s = divmod(the_time, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d:
        return "{0:.0f}d {1:.0f}h {2:.0f}m".format(d, h, m)
    elif h:
        return "{0:.0f}h {1:.0f}m {2:.0f}s".format(h, m, s)
    elif m:
        return "{0:.0f}m {1:.0f}s".format(m, s)
    else:
        return "{0:.0f}s".format(s)


def size_format(the_size):
    """"""
    kb_size = float(the_size) / 1024
    mb_size = float(kb_size) / 1024
    gb_size = float(mb_size) / 1024
    if gb_size > 1: #si son GB
        return "{0:.2f}GB".format(gb_size)
    elif mb_size > 1: #si son MB
        return "{0:.0f}MB".format(mb_size)
    elif kb_size > 1: #si no deben ser KB.
        return "{0:.0f}KB".format(kb_size)
    else: #si no deben ser B.
        return "{0:.0f}Bytes".format(the_size)


def speed_format(the_speed):
    """"""
    kb_speed = float(the_speed) / 1024
    mb_speed = float(kb_speed) / 1024
    gb_speed = float(mb_speed) / 1024
    if gb_speed > 1: #si son GB
        return "{0:.2f}GB/s".format(gb_speed)
    elif mb_speed > 1: #si son MB
        return "{0:.2f}MB/s".format(mb_speed)
    elif kb_speed > 1: #si no deben ser KB.
        return "{0:.0f}KB/s".format(kb_speed)
    else: #si no deben ser B.
        return "{0:.0f}Bytes/s".format(the_speed)


def get_filename_from_url(url):
    return os.path.split(url)[-1].split("?")[0]


def strip(input, to_strip=None):
    #to_strip: a string/list of chars you want to strip
    for x in to_strip or []:
        input = input.replace(x, '')
    return input


def normalize_file_name(name):
    name = html_entities_parser(name)
    name = urllib.unquote_plus(name)
    name = smart_unicode(name)
    name = strip(name, to_strip='/\\:*?"<>|')
    name = name.strip('.')
    return name


def tail(fh, lines_limit=20):
    """
    Read file from bottom to top (on reverse)
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
            #file too small, start from begining
            fh.seek(0, 0)
            # only read what was not read
            data.append(fh.read(bytes))
        lines_found = len(data[-1].splitlines()) #data[-1].count('\n')
        size -= lines_found
        bytes -= BUFSIZ
        block -= 1
    data.reverse() #put in right order.
    return '\n'.join(''.join(data).splitlines()[-lines_limit:])


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
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def url_unescape(url):
    entities = {
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": "\"",
        # must do ampersand last
        "&amp;": "&",
    }
    for k, v in entities.iteritems():
        url = url.replace(k, v)
    return url


def dict_from_cookiejar(cj):
    """
    Make a dict from a cookiejar and return it.
    """
    cookie_dict = {}
    for _, cookies in cj._cookies.items():
        for _, cookies in cookies.items():
            for cookie in cookies.values():
                cookie_dict[cookie.name] = cookie.value
    return cookie_dict


def load_cookie(path):
        cj = cookielib.MozillaCookieJar()
        cj.magic_re = ''  # fixes LoadError, netscape header comment checking.
        try:
            cj.load(path)
        except Exception as err:
            logger.warning(err)
            return None
        else:
            return cj


if __name__ == "__main__":
    pass
