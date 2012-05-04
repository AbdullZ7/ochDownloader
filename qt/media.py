import os
import sys
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons

from PySide.QtGui import *
from PySide.QtCore import *


#constants
EXT = ".png"

#sizes
SMALL = "16"
MEDIUM = "24"
LARGE = "48"
SCALABLE = "scalable"

#icons
ARROW_DOWN = "arrow_down_black"
PREFERENCES = "preferences"
START = "start"
STOP = "stop"
ACCOUNTS = "accounts"
ABOUT = "about"
ADD = "add"
DOWN = "down"
REFRESH = "view-refresh"
QUEUE = "queue"
CHECK = "check"
X_MARK = "x-mark"


def get_icon(img, size):
    return QIcon(os.path.join(cons.MEDIA_PATH, size, img))
    
def get_pixmap(img, size):
    return QPixmap(os.path.join(cons.MEDIA_PATH, size, img))

    
    
