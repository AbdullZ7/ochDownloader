import os

import core.cons as cons

from PySide.QtGui import *
from PySide.QtCore import *


class About(QMessageBox):
    def __init__(self, parent=None):
        QMessageBox.__init__(self, parent)
        self.setWindowTitle(_('About'))
        
        self.setIconPixmap(QPixmap(os.path.join(cons.MEDIA_PATH, "misc", "ochdownload.png")))
        
        header = '<font size="8"><b>' + cons.APP_NAME + '</b></font>'
        header += '&nbsp;&nbsp;&nbsp;'
        header += '<font size="6">' + cons.APP_VER + '</font>'
        self.setText(header)
        
        detail = '<p align="center">' + _('ochDownloader is a simple tool for One Click Hoster automated download') + '</p>'
        detail += '<p align="center"><font size="2">Copyright (c) 2011-2012 ochDownloader.com</font></p>'
        detail += '<p align="center"><a href="http://ochdownloader.com">www.ochdownloader.com</a></p>'
        self.setInformativeText(detail)
        
        self.exec_()
