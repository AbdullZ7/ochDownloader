import pygtk
import gtk
import gobject

import pkgutil
import os
import HTMLParser
import logging #registro de errores, van a consola y al fichero de texto.
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
import core.misc as misc
from core.plugins_parser import plugins_parser


def check_text(clipboard, selection_data):
    """"""
    urls = []
    tmp = clipboard.wait_for_text()
    if tmp:
        urls = misc.links_parser(tmp)
        #for line in tmp.splitlines():
            #if "http://" in line:
                #urls.append(line.strip())
    return urls

def check_contents(clipboard, selection_data):
    """"""
    if cons.OS_OSX:
        return check_osx_html(clipboard, selection_data)
    elif cons.OS_WIN:
        return check_html(clipboard, selection_data, "HTML Format", "utf8")
    else:
        return check_html(clipboard, selection_data, "text/html", "utf16")

def check_osx_html(clipboard, selection_data):
    """"""
    urls = []
    target = "public.rtf"
    if target  in list(selection_data):
        selection = clipboard.wait_for_contents(target)
        if selection:
            for line in str(selection.data.decode("utf8", "ignore")).splitlines():
                if '{HYPERLINK "' in line:
                    urls.append(line.split('{HYPERLINK "')[1].split('"}')[0])
    return urls

def check_html(clipboard, selection_data, target, codec):
    """"""
    urls = []
    if target in list(selection_data):
        selection = clipboard.wait_for_contents(target)
        if selection:
            for line in str(selection.data.decode(codec, "ignore")).splitlines():
                try:
                    parser = ClipParser()
                    parser.feed(line)
                except HTMLParser.HTMLParseError:
                    parser.reset()
                else:
                    urls += parser.urls
    return urls


class ClipParser(HTMLParser.HTMLParser):
    """"""
    def __init__(self):
        """"""
        HTMLParser.HTMLParser.__init__(self)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        """"""
        if tag == "a":
            for ref, link in attrs:
                if ref == "href":
                    self.urls.append(link)


class Clipboard:
    """"""
    def __init__(self, parent):
        """"""
        self.handler_id = None
        self.parent = parent
        self.enabled = False
        self.old_content = ""
        self.len_old = 0
        #self.monitor_open = False
        self.add_downloads = parent.add_downloads_gui #addDownloads class
        self.services = self.services()

    def services(self):
        """
        try:
            path_plugins = os.path.join(os.environ['_MEIPASS2'], 'plugins') #pyinstaller path.
        except KeyError:
            path_plugins = cons.PLUGINS_PATH
        services = [name for module_loader, name, ispkg in pkgutil.iter_modules(path=[path_plugins, ])]
        """
        #services = ["megaupload", ]
        services = plugins_parser.services_dict.keys()
        logger.debug("Services: {0}".format(services))
        return services

    def enable(self):
        """"""
        if cons.OS_WIN or cons.OS_OSX:
            self.enabled = True
            tmp = gtk.clipboard_get().wait_for_text()
            if tmp:
                self.old_content = tmp
                self.len_old = len(tmp)
            gobject.timeout_add_seconds(1, self.check_clipboard)
        else:
            self.handler_id = gtk.clipboard_get().connect("owner-change", self.poll_clipboard)
        return False

    def disable(self):
        """"""
        if cons.OS_WIN or cons.OS_OSX:
            self.enabled = False
        else:
            if self.handler_id:
                gtk.clipboard_get().disconnect(self.handler_id)

    def check_supported(self, urls):
        """"""
        links = []
        for url in urls:
            for name in self.services:
                if url.find(name) > 0:
                    links.append(url)
                    break
        return links

    def get_clipboard_links(self, clipboard, selection_data, data):
        """"""
        #html_links = self.check_supported(check_contents(clipboard, selection_data))
        text_links = self.check_supported(check_text(clipboard, selection_data))
        if text_links: # or html_links: #lists
            #http://www.megaupload.com/?d=ggu
            self.add_downloads.checking_links(text_links)
        #self.monitor_open = False

    def check_clipboard(self):
        """Windows and OSX support"""
        #if not self.monitor_open:
        clipboard = gtk.clipboard_get()
        tmp = clipboard.wait_for_text()
        if tmp:
            len_tmp = len(tmp)
            if len(tmp) != self.len_old:
                self.old_content = tmp
                self.len_old = len_tmp
                self.poll_clipboard(clipboard)
            else:
                for i in range(len_tmp):
                    if tmp[i] != self.old_content[i]:
                        self.old_content = tmp
                        self.len_old = len_tmp
                        self.poll_clipboard(clipboard)
                        break
        if self.enabled:
            return True

    def poll_clipboard(self, clipboard, event=None):
        """"""
        #if not self.monitor_open:
            #self.monitor_open = True
        clipboard.request_targets(self.get_clipboard_links)

