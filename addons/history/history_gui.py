import os
import logging
logger = logging.getLogger(__name__)

from core import utils

from PySide.QtGui import *
from PySide.QtCore import *

from qt.list_model import SimpleListModel
from qt.context_menu import Menu


class HistoryTab(QVBoxLayout):
    """"""
    def __init__(self, history_cls):
        """"""
        #TODO: cargar solo la lista al cambiar de pestania. no destruir todo.
        QVBoxLayout.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.history_cls = history_cls
        
        self.limit = 50
        self.offset = 0
        
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(10)
        
        self.search_entry = QLineEdit()
        self.search_entry.returnPressed.connect(self.on_search)
        self.search_entry.setFixedHeight(35)
        self.search_entry.setMinimumWidth(1)
        
        hbox.addWidget(self.search_entry)
        
        btn_search = QPushButton(_("Search"))
        btn_search.clicked.connect(self.on_search)
        btn_search.setDefault(True)
        btn_search.setFixedHeight(35)
        btn_search.setMaximumWidth(80)
        hbox.addWidget(btn_search)
        
        self.addLayout(hbox)
        
        self.btn_pre = QPushButton(_("Previous"))
        self.btn_pre.setFixedHeight(25)
        self.btn_pre.clicked.connect(self.on_previous)
        self.addWidget(self.btn_pre)
        
        self.tree_view = QTreeView()
        #
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.context_menu)
        #
        #listview look
        self.tree_view.setWordWrap(True) #search textElideMode
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setIndentation(0)
        self.tree_view.setAlternatingRowColors(True)
        #
        self.items = []
        headers = ["hidden_id_item", _("File Name"), _("Size"), _("Complete"), _("Date Time"), _("Link"), _("Directory")]
        #
        self.__model = SimpleListModel(headers, self.items)
        self.tree_view.setModel(self.__model)
        self.tree_view.setColumnHidden(0, True)
        self.tree_view.doubleClicked.connect(self.on_double_click)
        #self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.addWidget(self.tree_view)
        
        self.btn_next = QPushButton(_("Next"))
        self.btn_next.setFixedHeight(25)
        self.btn_next.clicked.connect(self.on_next)
        self.addWidget(self.btn_next)
        
        #self.on_load_items()

    def get_selected_rows(self):
        """"""
        selected_rows = [index.row() for index in self.tree_view.selectionModel().selectedRows()]
        selected_rows.sort()
        return selected_rows

    def context_menu(self, position):
        indexes = self.tree_view.selectedIndexes()
        is_selection = True if indexes else False
        options = [(_('Open destination folder'), self.on_open_folder, is_selection),
                    (_('Copy link'), self.on_copy_link, is_selection),
                    None,
                    (_('Remove'), self.on_remove, is_selection)]
        menu = Menu(options)
        menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    def on_open_folder(self):
        rows = self.get_selected_rows()
        if rows:
            paths_list = {self.items[row_index][6] for row_index in rows}
            for folder_path in paths_list:
                utils.open_folder_window(folder_path)

    def on_copy_link(self):
        rows = self.get_selected_rows()
        if rows:
            links_list = [self.items[row_index][5] for row_index in rows]
            clipboard = QApplication.clipboard()
            clipboard.setText('\n'.join(links_list))

    def on_remove(self):
        #TODO: reload list
        rows = self.get_selected_rows()
        if rows:
            id_list = [self.items[row_index][0] for row_index in rows]
            self.history_cls.remove_rows(id_list)
            [self.__model.remove(row_index) for row_index in rows]

    def on_double_click(self, q_index):
        row_index = q_index.row()
        path = os.path.join(self.items[row_index][6], self.items[row_index][1])
        utils.run_file(path)

    def on_search(self):
        self.offset = 0
        self.on_load_items()
    
    def on_previous(self):
        self.offset -= self.limit #* 2
        self.on_load_items()
    
    def on_next(self):
        self.offset += self.limit
        self.on_load_items()
        #if data_list:
    
    def on_load_items(self): #TEST when the items are 50, 51
        """"""
        self.validate_request()
        self.btn_next.setEnabled(True)
        self.btn_pre.setEnabled(True)
        match_term = self.search_entry.text()
        data_list = self.history_cls.get_data(self.offset, self.limit, match_term)
        self.__model.clear()
        [self.__model.append((id, name, utils.size_format(size), utils.size_format(complete), date_.strftime("%d-%m-%y %H:%M"), link, path))
            for id, name, link, size, complete, path, date_ in data_list]
        if len(data_list) < self.limit:
            self.btn_next.setEnabled(False)
        if self.offset == 0:
            self.btn_pre.setEnabled(False)
        #if data_list:
            #self.offset += self.limit
    
    def set_limit(self, limit):
        self.new_limit = limit

    def validate_request(self):
        if self.offset < 0:
            self.offset = 0
        if self.limit <= 0:
            self.limit = 1
    
    def on_load(self):
        """"""
        self.on_load_items()
        self.search_entry.setFocus() #call after creating all of the other widgets.
        logger.debug("History Tab loaded")

    def on_close(self):
        pass
