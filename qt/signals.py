from PySide.QtGui import *
from PySide.QtCore import *


class Signals(QObject):
    #create signals on the fly
    switch_tab = Signal(int)
    store_items = Signal(list)

signals = Signals()