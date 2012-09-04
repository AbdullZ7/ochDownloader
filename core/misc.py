import os
#import platform
import ctypes
import re
import htmlentitydefs
import subprocess

import cons
import logging #registro de errores, van a consola y al fichero de texto.
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).


def keep_system_awake(stop=False):
    """
    Prevent from going to sleeping state.
    TODO: implement.
    """
    #UNTESTED. check if the system go to sleep if the process is terminated
    mode_dict = {"ES_AWAYMODE_REQUIRED": "0x00000040",
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

def open_folder_window(path):
    """"""
    try:
        if cons.OS_WIN:
            retcode = subprocess.call(["explorer", path])
            #if retcode >= 0: #all good.
        elif cons.OS_UNIX: #sys.platform == 'linux2'
            retcode = subprocess.call(["gnome-open", path])
        else: #mac
            retcode = subprocess.call(["open", path])
    except OSError as err:
        logger.warning(err)

def run_file(path):
    """"""
    try:
        if cons.OS_WIN:
            retcode = subprocess.call([path, ], shell=True)
            #if retcode >= 0: #all good.
    except OSError as err:
        logger.warning(err)

def links_parser(text_pasted):
    """
    NOT FOOL PROOF
    """
    #el primer string al dividir, esta vacio.
    result_list = []
    #links_list = text_pasted.split("http") #['://www.megaup.com/wawa', 'parte1:', '://www.megaup.com/wawa2']
    links_list = [link
                    for line in text_pasted.splitlines()
                    for link in line.split("http")] #['parte1:http://www....', ]
    for link in links_list:
        if link.startswith("://") or link.startswith("s://"): #https
            result_list.append("".join(("http", link)).strip())
    return result_list

def smartdecode(s):
    """
    Not pretty smart, just try and error. It only covers utf-8 and latin-1
    """
    try:
        s = s.decode('utf-8')
    except UnicodeDecodeError:
        try:
            s = s.decode('latin-1') #will decode anything, even if it's not latin-1 (with weird characters in that case, tough)
        except UnicodeDecodeError as err:
            logger.exception("{0}: {1}".format(s[:30], err))
    return s #.encode("utf-8", "replace")

def time_format(the_time):
    """
    BUG: seconds go from 1 to 60, etc... dont remember. Should be from 0 to 59...
    """
    m, s = divmod(the_time, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d: return "{0:.0f}d {1:.0f}h {2:.0f}m".format(d, h, m)
    elif h: return "{0:.0f}h {1:.0f}m {2:.0f}s".format(h, m, s)
    elif m: return "{0:.0f}m {1:.0f}s".format(m, s)
    else: return "{0:.0f}s".format(s)
    #return "{0:0>2.0f}:{1:0>2.0f}:{2:0>2.0f}".format(h, m, s)

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

def get_host(link):
    """"""
    #assert link.startswith("http://"), ("'{0}' is not an url".format(link))
    i = 2 if link.startswith("http://") or link.startswith("https://") else 0
    host = link.split("/")[i] #get (www.)website.com
    host = host.split(".")[1] if host.startswith("www.") else host.split(".")[0] #get website
    return host.lower()

def get_filename_from_url(url):
    return os.path.split(url)[-1].split("?")[0]

def strip(input, to_strip=None):
    #strip: a string/list of chars you want to strip
    for x in to_strip or []:
        input = input.replace(x, '')
    return input

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

def dict_from_cookiejar(cj):
    """
    Make a dict from a cookiejar and return it.
    """
    cookie_dict = {}
    for _, cookies in cj._cookies.items():
        for _, cookies in cookies.items():
            for cookie in cookies.values():
                # print cookie
                cookie_dict[cookie.name] = cookie.value
    return cookie_dict


if __name__ == "__main__":
    pass
