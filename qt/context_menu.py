
from PySide.QtGui import *
from PySide.QtCore import *


class Menu(QMenu):
    """"""
    def __init__(self, parent, option_list):
        """"""
        QMenu.__init__(self, parent)
        for option in option_list:
            if option is None:
                self.addSeparator()
            else:
                title, callback, is_sensitive = option
                self.addAction(title, callback).setEnabled(is_sensitive)
