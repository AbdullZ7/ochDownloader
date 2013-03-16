
from PySide.QtGui import *
from PySide.QtCore import *

from .list_model import SimpleListModel


class TreeView(QTreeView):
    def __init__(self, headers):
        QTreeView.__init__(self)

        # listview look
        self.setWordWrap(True) # search textElideMode
        self.setRootIsDecorated(False)
        self.setIndentation(0)
        self.setAlternatingRowColors(True)

        self.items = []
        self.rows_buffer = {} # {id_item: row_obj, }

        self.model = SimpleListModel(headers, self.items)
        self.setModel(self.model)

    def remove_row(self, id_item):
        item = self.rows_buffer.pop(id_item)
        self.__model.remove(self.items.index(item))

    def get_selected_rows(self):
        selected_rows = [index.row() for index in self.selectionModel().selectedRows()]
        selected_rows.sort()
        return selected_rows

    def append_item(self, item):
        # item = [id, attr1, attr2, ]
        item = list(item)
        self.model.append(item)
        self.rows_buffer[item[0]] = item