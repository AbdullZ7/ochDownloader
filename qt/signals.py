from PySide.QtGui import *
from PySide.QtCore import *


class Signals(QObject):
    #create signals on the fly
    switch_tab = Signal(int)
    store_items = Signal(list)
    add_downloads_to_check = Signal(list)
    on_stop_all = Signal()
    status_bar_pop_msg = Signal(str)
    status_bar_push_msg = Signal(str)
    captured_links_count = Signal(int)

signals = Signals()