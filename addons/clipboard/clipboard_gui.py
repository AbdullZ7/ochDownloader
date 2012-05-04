import pkgutil
import os
import HTMLParser
import logging #registro de errores, van a consola y al fichero de texto.
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
import core.misc as misc
from core.plugins_parser import plugins_parser

from PySide.QtGui import *
from PySide.QtCore import *


class Clipboard:
    """"""
    def __init__(self, parent):
        """"""
        self.parent = parent
        self.text_old= ""
        self.len_old = 0
        self.add_downloads = parent.add_downloads #addDownloads class
        self.services = self.services()
        self.clipboard = QApplication.clipboard()

    def services(self):
        """"""
        services = plugins_parser.services_dict.keys()
        logger.debug("Services: {0}".format(services))
        return services

    def enable(self):
        """"""
        self.clipboard.dataChanged.connect(self.set_links)

    def disable(self):
        """"""
        self.clipboard.dataChanged.disconnect(self.set_links)
    
    def set_links(self):
        text = self.clipboard.text()
        if len(text) != self.len_old or text != self.text_old:
            urls = self.check_supported(self.check_text(text))
            if urls:
                self.add_downloads.links_checking(urls)
            self.len_old = len(text)
            self.text_old = text

    def check_text(self, text):
        urls = []
        if text:
            urls = misc.links_parser(text)
        return urls

    def check_supported(self, urls):
        """"""
        links = []
        for url in urls:
            for name in self.services:
                if url.find(name) > 0:
                    links.append(url)
                    break
        return links
